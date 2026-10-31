"""Works out where a task can move, and moves it. Used by the assistant; checks every rule."""

import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from yadi.modules.preferences.router import UserPreferences
from yadi.modules.reminders.sync import sync_reminders
from yadi.modules.scheduling import engine
from yadi.modules.scheduling.models import ScheduleBlock
from yadi.modules.tasks.lifecycle import TaskStatus
from yadi.modules.tasks.models import Task, TaskEvent

PLANNABLE = (TaskStatus.INBOX.value, TaskStatus.PLANNED.value)


class MoveRefused(Exception):
    """The move cannot happen. The message says why, for the user."""


@dataclass(frozen=True)
class MovePlan:
    start: datetime
    end: datetime
    past_deadline: bool
    clashes: tuple[str, ...]


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise MoveRefused("Which day do you mean?") from exc


def parse_time(value: str | None) -> time | None:
    if value is None:
        return None
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise MoveRefused("What time do you mean?") from exc


def _future_blocks(session: Session, task_id: uuid.UUID, now: datetime) -> list[ScheduleBlock]:
    return list(
        session.scalars(
            select(ScheduleBlock)
            .where(ScheduleBlock.task_id == task_id, ScheduleBlock.end_at > now)
            .order_by(ScheduleBlock.start_at)
        ).all()
    )


def _other_blocks(
    session: Session, user_id: uuid.UUID, task_id: uuid.UUID, now: datetime
) -> list[tuple[engine.Interval, str]]:
    rows = session.execute(
        select(ScheduleBlock.start_at, ScheduleBlock.end_at, Task.title)
        .join(Task, Task.id == ScheduleBlock.task_id)
        .where(
            ScheduleBlock.user_id == user_id,
            ScheduleBlock.task_id != task_id,
            ScheduleBlock.end_at > now,
        )
    ).all()
    return [(engine.Interval(start, end), title) for start, end, title in rows]


def _plan_fixed(
    session: Session, task: Task, day: date, at: time | None, zone: ZoneInfo, now: datetime
) -> MovePlan:
    assert task.fixed_start_at and task.fixed_end_at
    if at is None:
        raise MoveRefused(f'What time should "{task.title}" start?')
    start = datetime.combine(day, at, zone).astimezone(UTC)
    if start <= now:
        raise MoveRefused("That time has already passed.")
    end = start + (task.fixed_end_at - task.fixed_start_at)
    moved = engine.Interval(start, end)
    others = _other_blocks(session, task.user_id, task.id, now)
    clashes = tuple(
        sorted({title for other, title in others if moved.start < other.end and other.start < end})
    )
    return MovePlan(start, end, False, clashes)


def plan_move(
    session: Session,
    task: Task,
    *,
    target_date: date | None,
    period: str | None,
    target_time: time | None,
    now: datetime,
) -> MovePlan:
    prefs = session.get_one(UserPreferences, task.user_id)
    zone = ZoneInfo(prefs.timezone)
    blocks = _future_blocks(session, task.id, now)
    if target_date is None and target_time is None and period is None:
        raise MoveRefused(f'When should "{task.title}" move to?')
    current = (task.fixed_start_at or (blocks[0].start_at if blocks else now)).astimezone(zone)
    # "Move it to the afternoon" means the same day if that is still possible.
    day = target_date or max(current.date(), now.astimezone(zone).date())
    if day < now.astimezone(zone).date():
        raise MoveRefused("That day has already passed.")
    if task.fixed_start_at:
        return _plan_fixed(session, task, day, target_time, zone, now)

    minutes = sum(int((b.end_at - b.start_at).total_seconds() // 60) for b in blocks)
    minutes = minutes or (task.estimated_minutes or 0)
    if minutes == 0:
        raise MoveRefused(f'How long will "{task.title}" take? Add an estimate, then ask again.')

    day_start = datetime.combine(day, time(0), zone).astimezone(UTC)
    whole_day = engine.Interval(max(day_start, now), day_start + timedelta(hours=26))
    opening = engine.local_windows(whole_day, prefs.timezone, prefs.work_start, prefs.work_end)
    free = [item for item in opening if item.start.astimezone(zone).date() == day]
    if not free:
        raise MoveRefused(f"There are no working hours left on {day:%a %d %b}.")
    gap = timedelta(minutes=prefs.buffer_minutes)
    for other, _ in _other_blocks(session, task.user_id, task.id, now):
        free = engine.subtract(free, engine.Interval(other.start - gap, other.end + gap))

    length = timedelta(minutes=minutes)
    if target_time is not None:
        start = datetime.combine(day, target_time, zone).astimezone(UTC)
        if start <= now:
            raise MoveRefused("That time has already passed.")
        if not any(i.start <= start and start + length <= i.end for i in free):
            raise MoveRefused(
                f"{minutes} minutes at {target_time:%H:%M} on {day:%a %d %b} does not fit: it is "
                "outside your working hours or overlaps something else."
            )
    else:
        if period is not None:
            period_start, period_end = engine.PERIODS[period]
            window = engine.Interval(
                datetime.combine(day, period_start, zone).astimezone(UTC),
                datetime.combine(day, period_end, zone).astimezone(UTC),
            )
            free = [
                engine.Interval(max(i.start, window.start), min(i.end, window.end))
                for i in free
                if i.start < window.end and window.start < i.end
            ]
        slot = next((i for i in free if i.minutes >= minutes), None)
        if slot is None:
            where = f"the {period} of {day:%a %d %b}" if period else f"{day:%a %d %b}"
            raise MoveRefused(f"{minutes} free minutes in a row are not available on {where}.")
        start = slot.start
    end = start + length
    late = task.due_at is not None and end > task.due_at
    return MovePlan(start, end, late, ())


def apply_move(session: Session, task: Task, plan: MovePlan, now: datetime) -> None:
    """Replaces the task's future blocks with one the user asked for. Commits."""
    session.execute(
        delete(ScheduleBlock).where(ScheduleBlock.task_id == task.id, ScheduleBlock.end_at > now)
    )
    is_fixed = task.fixed_start_at is not None
    if is_fixed:
        task.fixed_start_at, task.fixed_end_at = plan.start, plan.end
        task.updated_at = now
    session.add(
        ScheduleBlock(
            user_id=task.user_id,
            task_id=task.id,
            start_at=plan.start,
            end_at=plan.end,
            is_fixed=is_fixed,
            locked=True,
            reason=(
                "A fixed commitment. Yadi plans around it and never moves it."
                if is_fixed
                else "You asked for this time. Yadi keeps it when replanning."
            ),
        )
    )
    if task.status in PLANNABLE:
        task.status = TaskStatus.SCHEDULED.value
    session.add(
        TaskEvent(
            task_id=task.id,
            user_id=task.user_id,
            type="rescheduled",
            actor="ai",
            payload={"start": plan.start.isoformat(), "end": plan.end.isoformat()},
        )
    )
    sync_reminders(session, task.user_id, [task], now)
    session.commit()
