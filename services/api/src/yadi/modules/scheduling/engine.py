"""The scheduling engine. Pure and deterministic: no database, no clock, no AI (ADR-004).

Greedy: place fixed work, then give each flexible task the earliest time that works, tightest
deadline first. Work that cannot fit is reported, never squeezed in.
"""

import heapq
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
PERIODS = {
    "morning": (time(5), time(12)),
    "afternoon": (time(12), time(17)),
    "evening": (time(17), time(22)),
}

NO_ESTIMATE = "NO_ESTIMATE"
NO_CAPACITY_BEFORE_DEADLINE = "NO_CAPACITY_BEFORE_DEADLINE"
OUTSIDE_WINDOW = "OUTSIDE_WINDOW"
DEPENDENCY_UNSCHEDULED = "DEPENDENCY_UNSCHEDULED"
DEPENDENCY_CYCLE = "DEPENDENCY_CYCLE"


@dataclass(frozen=True)
class Interval:
    start: datetime
    end: datetime

    @property
    def minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


@dataclass(frozen=True)
class TaskInput:
    id: uuid.UUID
    title: str
    priority: str
    due_at: datetime | None
    estimated_minutes: int | None
    preferred_period: str | None
    created_at: datetime
    depends_on: tuple[uuid.UUID, ...] = ()


@dataclass(frozen=True)
class BusyBlock:
    """Time that cannot be used: a fixed event or a block the user locked."""

    task_id: uuid.UUID
    title: str
    interval: Interval


@dataclass(frozen=True)
class ScheduleInput:
    tasks: tuple[TaskInput, ...]
    fixed: tuple[BusyBlock, ...]
    locked: tuple[BusyBlock, ...]
    timezone: str
    work_start: time
    work_end: time
    buffer_minutes: int
    window: Interval
    now: datetime
    min_chunk_minutes: int = 25


@dataclass(frozen=True)
class PlannedBlock:
    task_id: uuid.UUID
    interval: Interval
    reason: str


@dataclass(frozen=True)
class UnscheduledTask:
    task_id: uuid.UUID
    title: str
    reason: str
    detail: str
    alternatives: tuple[str, ...]


@dataclass(frozen=True)
class FixedConflict:
    first_title: str
    second_title: str
    interval: Interval


@dataclass(frozen=True)
class ScheduleResult:
    blocks: tuple[PlannedBlock, ...]
    unscheduled: tuple[UnscheduledTask, ...]
    conflicts: tuple[FixedConflict, ...]


def local_windows(window: Interval, timezone: str, start: time, end: time) -> list[Interval]:
    """One interval per local day, in UTC. Wall-clock based, so daylight-saving days are correct."""
    zone = ZoneInfo(timezone)
    day = window.start.astimezone(zone).date()
    last = window.end.astimezone(zone).date()
    result = []
    while day <= last:
        opens = datetime.combine(day, start, zone).astimezone(UTC)
        closes = datetime.combine(day, end, zone).astimezone(UTC)
        clipped = Interval(max(opens, window.start), min(closes, window.end))
        if clipped.start < clipped.end:
            result.append(clipped)
        day += timedelta(days=1)
    return result


def subtract(free: list[Interval], busy: Interval) -> list[Interval]:
    result = []
    for item in free:
        if busy.end <= item.start or busy.start >= item.end:
            result.append(item)
            continue
        if item.start < busy.start:
            result.append(Interval(item.start, busy.start))
        if busy.end < item.end:
            result.append(Interval(busy.end, item.end))
    return result


def _take(
    free: list[Interval],
    minutes: int,
    earliest: datetime,
    latest: datetime | None,
    min_chunk: int,
) -> tuple[list[Interval], int]:
    """Earliest chunks covering `minutes`. Returns the chunks and the minutes still missing."""
    chunks: list[Interval] = []
    remaining = minutes
    for item in free:
        if remaining == 0:
            break
        start = max(item.start, earliest)
        end = min(item.end, latest) if latest else item.end
        if end <= start:
            continue
        available = Interval(start, end).minutes
        if available >= remaining:
            take = remaining
        else:
            # Never leave a remainder too small to be a useful chunk of its own.
            take = min(available, remaining - min_chunk)
            if take < min_chunk:
                continue
        chunks.append(Interval(start, start + timedelta(minutes=take)))
        remaining -= take
    return chunks, remaining


def _ordered_tasks(
    tasks: list[TaskInput], now: datetime
) -> tuple[list[TaskInput], list[TaskInput]]:
    """Dependency order, then least slack, priority, age. Returns (ordered, in a cycle)."""

    def key(task: TaskInput) -> tuple[int, float, int, datetime, str]:
        if task.due_at is None:
            has_deadline, slack = 1, 0.0
        else:
            needed = (task.estimated_minutes or 0) * 60
            has_deadline, slack = 0, (task.due_at - now).total_seconds() - needed
        return (has_deadline, slack, PRIORITY_ORDER[task.priority], task.created_at, str(task.id))

    by_id = {task.id: task for task in tasks}
    waiting = {
        task.id: {dep for dep in task.depends_on if dep in by_id and dep != task.id}
        for task in tasks
    }
    dependents: dict[uuid.UUID, list[uuid.UUID]] = {task.id: [] for task in tasks}
    for task_id, deps in waiting.items():
        for dep in deps:
            dependents[dep].append(task_id)

    heap = [(key(by_id[task_id]), task_id) for task_id, deps in waiting.items() if not deps]
    heapq.heapify(heap)
    ordered = []
    while heap:
        _, task_id = heapq.heappop(heap)
        ordered.append(by_id[task_id])
        for dependent in dependents[task_id]:
            waiting[dependent].discard(task_id)
            if not waiting[dependent]:
                heapq.heappush(heap, (key(by_id[dependent]), dependent))
    placed = {task.id for task in ordered}
    return ordered, [task for task in tasks if task.id not in placed]


def _find_conflicts(fixed: tuple[BusyBlock, ...]) -> tuple[FixedConflict, ...]:
    items = sorted(fixed, key=lambda block: (block.interval.start, str(block.task_id)))
    conflicts = []
    for index, first in enumerate(items):
        for second in items[index + 1 :]:
            if second.interval.start >= first.interval.end:
                break
            overlap = Interval(second.interval.start, min(first.interval.end, second.interval.end))
            conflicts.append(FixedConflict(first.title, second.title, overlap))
    return tuple(conflicts)


def _reason(task: TaskInput, used_preferred: bool, zone: ZoneInfo) -> str:
    parts = []
    if task.due_at:
        parts.append(
            f"Due {task.due_at.astimezone(zone):%a %d %b %H:%M}, so it goes before later work"
        )
    else:
        parts.append("No deadline, so it uses open time after work with deadlines")
    if used_preferred:
        parts.append(f"placed in your preferred {task.preferred_period}")
    if task.priority in ("critical", "high"):
        parts.append(f"{task.priority} priority")
    return "; ".join(parts) + "."


def _deadline_passed(task: TaskInput) -> UnscheduledTask:
    return UnscheduledTask(
        task.id,
        task.title,
        NO_CAPACITY_BEFORE_DEADLINE,
        "The deadline has already passed.",
        ("Set a new deadline", "Complete or cancel it if it no longer applies"),
    )


def _no_fit(
    task: TaskInput, missing: int, placed: list[PlannedBlock], titles: dict[uuid.UUID, TaskInput]
) -> UnscheduledTask:
    lower = sorted(
        {
            titles[block.task_id].title
            for block in placed
            if PRIORITY_ORDER[titles[block.task_id].priority] > PRIORITY_ORDER[task.priority]
        }
    )
    alternatives = [f"Free up {missing} more minutes", "Shorten the estimate"]
    if task.due_at:
        reason = NO_CAPACITY_BEFORE_DEADLINE
        detail = f"{missing} of {task.estimated_minutes} minutes do not fit before the deadline."
        alternatives.insert(0, "Move the deadline later")
    else:
        reason = OUTSIDE_WINDOW
        detail = (
            f"{missing} of {task.estimated_minutes} minutes do not fit in this planning period."
        )
        alternatives.insert(0, "Plan further ahead")
    alternatives += [f"Postpone {title}" for title in lower[:3]]
    return UnscheduledTask(task.id, task.title, reason, detail, tuple(alternatives))


def _round_up(moment: datetime, minutes: int = 5) -> datetime:
    step = minutes * 60
    seconds = moment.timestamp()
    return datetime.fromtimestamp((seconds + step - 1e-6) // step * step, UTC)


def generate_schedule(data: ScheduleInput) -> ScheduleResult:
    zone = ZoneInfo(data.timezone)
    opening = Interval(max(data.window.start, _round_up(data.now)), data.window.end)
    free = local_windows(opening, data.timezone, data.work_start, data.work_end)
    buffer = timedelta(minutes=data.buffer_minutes)

    def block_out(free_time: list[Interval], interval: Interval) -> list[Interval]:
        return subtract(free_time, Interval(interval.start - buffer, interval.end + buffer))

    for busy in (*data.fixed, *data.locked):
        free = block_out(free, busy.interval)

    locked_minutes: dict[uuid.UUID, int] = {}
    ends: dict[uuid.UUID, datetime] = {}
    for busy in data.locked:
        locked_minutes[busy.task_id] = locked_minutes.get(busy.task_id, 0) + busy.interval.minutes
        ends[busy.task_id] = max(ends.get(busy.task_id, busy.interval.end), busy.interval.end)
    for busy in data.fixed:
        ends[busy.task_id] = max(ends.get(busy.task_id, busy.interval.end), busy.interval.end)

    by_id = {task.id: task for task in data.tasks}
    ordered, cyclic = _ordered_tasks(list(data.tasks), data.now)
    planned: list[PlannedBlock] = []
    unscheduled: dict[uuid.UUID, UnscheduledTask] = {}

    for task in cyclic:
        unscheduled[task.id] = UnscheduledTask(
            task.id,
            task.title,
            DEPENDENCY_CYCLE,
            "This task and another each wait for the other.",
            ("Remove one of the dependencies",),
        )

    for task in ordered:
        if task.estimated_minutes is None:
            unscheduled[task.id] = UnscheduledTask(
                task.id,
                task.title,
                NO_ESTIMATE,
                "Yadi needs to know how long this will take.",
                ("Add an estimate",),
            )
            continue
        blockers = [
            dep
            for dep in task.depends_on
            if dep in unscheduled or (dep in by_id and dep not in ends and dep != task.id)
        ]
        if blockers:
            names = ", ".join(sorted(by_id[dep].title for dep in blockers if dep in by_id))
            unscheduled[task.id] = UnscheduledTask(
                task.id,
                task.title,
                DEPENDENCY_UNSCHEDULED,
                f"It must wait for {names}, which is not scheduled.",
                (f"Schedule {names} first",),
            )
            continue

        if task.due_at and task.due_at <= data.now:
            unscheduled[task.id] = _deadline_passed(task)
            continue
        minutes = task.estimated_minutes - locked_minutes.get(task.id, 0)
        if minutes <= 0:
            continue
        earliest = max([opening.start, *(ends[dep] for dep in task.depends_on if dep in ends)])
        chunks: list[Interval] = []
        missing = minutes
        used_preferred = False
        if task.preferred_period:
            period_start, period_end = PERIODS[task.preferred_period]
            preferred: list[Interval] = []
            for period in local_windows(opening, data.timezone, period_start, period_end):
                preferred += [
                    Interval(max(item.start, period.start), min(item.end, period.end))
                    for item in free
                    if item.start < period.end and period.start < item.end
                ]
            chunks, missing = _take(
                preferred, minutes, earliest, task.due_at, data.min_chunk_minutes
            )
            used_preferred = missing == 0
        if not used_preferred:
            chunks, missing = _take(free, minutes, earliest, task.due_at, data.min_chunk_minutes)
        if missing > 0:
            unscheduled[task.id] = _no_fit(task, missing, planned, by_id)
            continue

        reason = _reason(task, used_preferred, zone)
        for chunk in chunks:
            planned.append(PlannedBlock(task.id, chunk, reason))
            free = block_out(free, chunk)
        ends[task.id] = max(chunk.end for chunk in chunks)

    return ScheduleResult(
        blocks=tuple(sorted(planned, key=lambda block: (block.interval.start, str(block.task_id)))),
        unscheduled=tuple(sorted(unscheduled.values(), key=lambda item: str(item.task_id))),
        conflicts=_find_conflicts(data.fixed),
    )
