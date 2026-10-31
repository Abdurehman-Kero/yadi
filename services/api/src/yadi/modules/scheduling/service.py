"""Connects the pure engine to stored data. Every query is scoped by user_id."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from yadi.core.errors import AppError
from yadi.modules.preferences.router import UserPreferences
from yadi.modules.reminders.sync import sync_reminders
from yadi.modules.scheduling import engine
from yadi.modules.scheduling.models import ScheduleBlock, ScheduleRun, TaskDependency
from yadi.modules.scheduling.schemas import (
    BlockOut,
    BlockUpdate,
    ConflictOut,
    ScheduleOut,
    UnscheduledOut,
)
from yadi.modules.tasks.lifecycle import TaskStatus, status_for_details
from yadi.modules.tasks.models import Task, TaskEvent
from yadi.modules.users.models import User

ACTIVE = (
    TaskStatus.INBOX.value,
    TaskStatus.PLANNED.value,
    TaskStatus.SCHEDULED.value,
    TaskStatus.IN_PROGRESS.value,
)
# Yadi may move these between each other; in_progress is the user's own statement.
PLANNABLE = (TaskStatus.INBOX.value, TaskStatus.PLANNED.value, TaskStatus.SCHEDULED.value)


def _active_tasks(session: Session, user_id: uuid.UUID) -> Sequence[Task]:
    return session.scalars(
        select(Task).where(Task.user_id == user_id, Task.status.in_(ACTIVE)).order_by(Task.id)
    ).all()


def _dependencies(
    session: Session, task_ids: list[uuid.UUID]
) -> dict[uuid.UUID, tuple[uuid.UUID, ...]]:
    rows = session.scalars(select(TaskDependency).where(TaskDependency.task_id.in_(task_ids))).all()
    result: dict[uuid.UUID, tuple[uuid.UUID, ...]] = {}
    for row in rows:
        result[row.task_id] = (*result.get(row.task_id, ()), row.depends_on_task_id)
    return result


def _set_scheduled_status(session: Session, task: Task, *, placed: bool) -> None:
    if task.status not in PLANNABLE:
        return
    if placed:
        target = TaskStatus.SCHEDULED
    else:
        target = status_for_details(
            has_due=task.due_at is not None,
            has_estimate=task.estimated_minutes is not None,
            has_fixed=task.fixed_start_at is not None,
        )
    if task.status == target.value:
        return
    previous = task.status
    task.status = target.value
    session.add(
        TaskEvent(
            task_id=task.id,
            user_id=task.user_id,
            type="scheduled" if placed else "unscheduled",
            actor="system",
            payload={"from": previous, "to": target.value},
        )
    )


def generate(session: Session, user_id: uuid.UUID, *, days: int, now: datetime) -> ScheduleOut:
    # One generation at a time per user, so two tabs cannot interleave their deletes and inserts.
    session.execute(select(User.id).where(User.id == user_id).with_for_update())
    prefs = session.get_one(UserPreferences, user_id)
    window = engine.Interval(now, now + timedelta(days=days))
    tasks = _active_tasks(session, user_id)
    by_id = {task.id: task for task in tasks}
    dependencies = _dependencies(session, list(by_id))

    locked_rows = session.scalars(
        select(ScheduleBlock).where(
            ScheduleBlock.user_id == user_id,
            ScheduleBlock.locked.is_(True),
            ScheduleBlock.is_fixed.is_(False),
            ScheduleBlock.end_at > now,
            ScheduleBlock.task_id.in_(list(by_id)),
        )
    ).all()
    session.execute(
        delete(ScheduleBlock).where(
            ScheduleBlock.user_id == user_id,
            ScheduleBlock.end_at > now,
            ScheduleBlock.id.not_in([row.id for row in locked_rows]),
        )
    )

    fixed_tasks = [t for t in tasks if t.fixed_start_at and t.fixed_end_at]
    fixed = tuple(
        engine.BusyBlock(t.id, t.title, engine.Interval(t.fixed_start_at, t.fixed_end_at))  # type: ignore[arg-type]
        for t in fixed_tasks
    )
    locked = tuple(
        engine.BusyBlock(
            row.task_id, by_id[row.task_id].title, engine.Interval(row.start_at, row.end_at)
        )
        for row in locked_rows
    )
    flexible = tuple(
        engine.TaskInput(
            id=t.id,
            title=t.title,
            priority=t.priority,
            due_at=t.due_at,
            estimated_minutes=t.estimated_minutes,
            preferred_period=t.preferred_period,
            created_at=t.created_at,
            depends_on=dependencies.get(t.id, ()),
        )
        for t in tasks
        if t.fixed_start_at is None
    )
    result = engine.generate_schedule(
        engine.ScheduleInput(
            tasks=flexible,
            fixed=fixed,
            locked=locked,
            timezone=prefs.timezone,
            work_start=prefs.work_start,
            work_end=prefs.work_end,
            buffer_minutes=prefs.buffer_minutes,
            window=window,
            now=now,
        )
    )

    for task in fixed_tasks:
        assert task.fixed_start_at and task.fixed_end_at
        if task.fixed_end_at > now:
            session.add(
                ScheduleBlock(
                    user_id=user_id,
                    task_id=task.id,
                    start_at=task.fixed_start_at,
                    end_at=task.fixed_end_at,
                    is_fixed=True,
                    locked=True,
                    reason="A fixed commitment. Yadi plans around it and never moves it.",
                )
            )
    for block in result.blocks:
        session.add(
            ScheduleBlock(
                user_id=user_id,
                task_id=block.task_id,
                start_at=block.interval.start,
                end_at=block.interval.end,
                reason=block.reason,
            )
        )

    unscheduled_ids = {item.task_id for item in result.unscheduled}
    for task in tasks:
        _set_scheduled_status(session, task, placed=task.id not in unscheduled_ids)

    sync_reminders(session, user_id, tasks, now)
    session.add(
        ScheduleRun(
            user_id=user_id,
            window_start=window.start,
            window_end=window.end,
            unscheduled=[
                {
                    "task_id": str(item.task_id),
                    "title": item.title,
                    "reason": item.reason,
                    "detail": item.detail,
                    "alternatives": list(item.alternatives),
                }
                for item in result.unscheduled
            ],
            conflicts=[
                {
                    "first_title": item.first_title,
                    "second_title": item.second_title,
                    "start_at": item.interval.start.isoformat(),
                    "end_at": item.interval.end.isoformat(),
                }
                for item in result.conflicts
            ],
        )
    )
    session.commit()
    zone = ZoneInfo(prefs.timezone)
    start_of_day = now.astimezone(zone).replace(hour=0, minute=0, second=0, microsecond=0)
    return read(session, user_id, start=start_of_day.astimezone(UTC), end=window.end)


def read(session: Session, user_id: uuid.UUID, *, start: datetime, end: datetime) -> ScheduleOut:
    rows = session.execute(
        select(ScheduleBlock, Task)
        .join(Task, Task.id == ScheduleBlock.task_id)
        .where(
            ScheduleBlock.user_id == user_id,
            ScheduleBlock.end_at > start,
            ScheduleBlock.start_at < end,
        )
        .order_by(ScheduleBlock.start_at, ScheduleBlock.id)
    ).all()
    blocks = [
        BlockOut(
            id=block.id,
            task_id=block.task_id,
            title=task.title,
            priority=task.priority,
            status=task.status,
            start_at=block.start_at,
            end_at=block.end_at,
            is_fixed=block.is_fixed,
            locked=block.locked,
            reason=block.reason,
        )
        for block, task in rows
    ]
    run = session.scalars(
        select(ScheduleRun)
        .where(ScheduleRun.user_id == user_id)
        .order_by(ScheduleRun.created_at.desc())
        .limit(1)
    ).first()
    if run is None:
        return ScheduleOut(
            blocks=blocks, unscheduled=[], conflicts=[], generated_at=None, stale=False
        )

    active_ids = {t.id for t in _active_tasks(session, user_id)}
    newest_change = session.scalar(select(func.max(Task.updated_at)).where(Task.user_id == user_id))
    return ScheduleOut(
        blocks=blocks,
        unscheduled=[
            UnscheduledOut.model_validate(item)
            for item in run.unscheduled
            if uuid.UUID(item["task_id"]) in active_ids
        ],
        conflicts=[ConflictOut.model_validate(item) for item in run.conflicts],
        generated_at=run.created_at,
        stale=newest_change is not None and newest_change > run.created_at,
    )


def _conflict(message: str) -> AppError:
    return AppError("CONFLICT", 409, message)


def update_block(
    session: Session, user_id: uuid.UUID, block_id: uuid.UUID, data: BlockUpdate
) -> None:
    """A manual change locks the block, so regeneration keeps the user's decision."""
    block = session.scalars(
        select(ScheduleBlock)
        .where(ScheduleBlock.id == block_id, ScheduleBlock.user_id == user_id)
        .with_for_update()
    ).first()
    if block is None:
        raise AppError("NOT_FOUND", 404, "Scheduled block not found.")
    if block.is_fixed:
        raise _conflict("This is a fixed commitment. Change it from the task instead.")
    if data.end_at <= data.start_at:
        details = [{"field": "endAt", "issue": "The end must be after the start."}]
        raise AppError("VALIDATION_FAILED", 400, "Invalid request.", details)

    prefs = session.get_one(UserPreferences, user_id)
    moved = engine.Interval(data.start_at.astimezone(UTC), data.end_at.astimezone(UTC))
    work = engine.local_windows(
        engine.Interval(moved.start - timedelta(days=1), moved.end + timedelta(days=1)),
        prefs.timezone,
        prefs.work_start,
        prefs.work_end,
    )
    if not any(w.start <= moved.start and moved.end <= w.end for w in work):
        raise _conflict("That time is outside your working hours.")
    clash = session.scalar(
        select(ScheduleBlock.id).where(
            ScheduleBlock.user_id == user_id,
            ScheduleBlock.id != block_id,
            ScheduleBlock.start_at < moved.end,
            ScheduleBlock.end_at > moved.start,
        )
    )
    if clash is not None:
        raise _conflict("That time overlaps something else in your schedule.")

    block.start_at, block.end_at = moved.start, moved.end
    block.locked = True
    block.reason = "You placed this here. Yadi keeps it when replanning."
    session.add(
        TaskEvent(
            task_id=block.task_id,
            user_id=user_id,
            type="rescheduled",
            actor="user",
            payload={"start": moved.start.isoformat(), "end": moved.end.isoformat()},
        )
    )
    sync_reminders(session, user_id, [session.get_one(Task, block.task_id)], datetime.now(UTC))
    session.commit()


def block_out(session: Session, user_id: uuid.UUID, block_id: uuid.UUID) -> BlockOut:
    block, task = session.execute(
        select(ScheduleBlock, Task)
        .join(Task, Task.id == ScheduleBlock.task_id)
        .where(ScheduleBlock.id == block_id, ScheduleBlock.user_id == user_id)
    ).one()
    return BlockOut(
        id=block.id,
        task_id=block.task_id,
        title=task.title,
        priority=task.priority,
        status=task.status,
        start_at=block.start_at,
        end_at=block.end_at,
        is_fixed=block.is_fixed,
        locked=block.locked,
        reason=block.reason,
    )


def set_dependencies(
    session: Session, user_id: uuid.UUID, task_id: uuid.UUID, depends_on: list[uuid.UUID]
) -> list[uuid.UUID]:
    wanted = set(depends_on)
    owned = set(
        session.scalars(
            select(Task.id).where(Task.user_id == user_id, Task.id.in_([task_id, *wanted]))
        ).all()
    )
    if task_id not in owned:
        raise AppError("NOT_FOUND", 404, "Task not found.")
    # An unknown or foreign id gets the same answer, so other users' task ids are not revealed.
    if not wanted <= owned:
        raise AppError("NOT_FOUND", 404, "A task it depends on was not found.")
    if task_id in wanted:
        raise _conflict("A task cannot depend on itself.")

    edges = session.execute(
        select(TaskDependency.task_id, TaskDependency.depends_on_task_id)
        .join(Task, Task.id == TaskDependency.task_id)
        .where(Task.user_id == user_id, TaskDependency.task_id != task_id)
    ).all()
    graph: dict[uuid.UUID, set[uuid.UUID]] = {}
    for source, target in edges:
        graph.setdefault(source, set()).add(target)
    stack, seen = list(wanted), set()
    while stack:
        current = stack.pop()
        if current == task_id:
            raise _conflict("That would make these tasks wait for each other.")
        if current not in seen:
            seen.add(current)
            stack.extend(graph.get(current, ()))

    session.execute(delete(TaskDependency).where(TaskDependency.task_id == task_id))
    session.add_all(TaskDependency(task_id=task_id, depends_on_task_id=d) for d in sorted(wanted))
    task = session.get_one(Task, task_id)
    task.updated_at = datetime.now(UTC)
    session.commit()
    return sorted(wanted)


def get_dependencies(session: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> list[uuid.UUID]:
    if session.scalar(select(Task.id).where(Task.id == task_id, Task.user_id == user_id)) is None:
        raise AppError("NOT_FOUND", 404, "Task not found.")
    return sorted(
        session.scalars(
            select(TaskDependency.depends_on_task_id).where(TaskDependency.task_id == task_id)
        ).all()
    )
