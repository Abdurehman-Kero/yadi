"""Keeps a task's automatic reminder in step with it, inside the caller's transaction."""

import hashlib
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from yadi.modules.preferences.router import UserPreferences
from yadi.modules.reminders.models import Reminder
from yadi.modules.scheduling.models import ScheduleBlock
from yadi.modules.tasks.lifecycle import TaskStatus
from yadi.modules.tasks.models import Task

FINISHED = (TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value)


@dataclass(frozen=True)
class Anchor:
    kind: str  # "start" or "due"
    at: datetime


def choose_anchor(task: Task, first_block: datetime | None, now: datetime) -> Anchor | None:
    """The moment the reminder points at: fixed start, else planned start, else deadline."""
    if task.status in FINISHED or not task.reminder_enabled:
        return None
    if task.status != TaskStatus.IN_PROGRESS.value:
        if task.fixed_start_at and task.fixed_start_at > now:
            return Anchor("start", task.fixed_start_at)
        if first_block and first_block > now:
            return Anchor("start", first_block)
    if task.due_at and task.due_at > now:
        return Anchor("due", task.due_at)
    return None


def reminder_key(*parts: object) -> str:
    # Built from the plan, never the current clock, so recalculating cannot create a duplicate.
    return hashlib.sha256("|".join(str(part) for part in parts).encode()).hexdigest()


def sync_reminders(
    session: Session, user_id: uuid.UUID, tasks: Sequence[Task], now: datetime
) -> None:
    """Cancels what no longer applies and creates what is missing. Does not commit."""
    if not tasks:
        return
    session.flush()
    default_minutes = session.get_one(UserPreferences, user_id).default_reminder_minutes
    rows = session.execute(
        select(ScheduleBlock.task_id, func.min(ScheduleBlock.start_at))
        .where(
            ScheduleBlock.task_id.in_([task.id for task in tasks]),
            ScheduleBlock.start_at > now,
        )
        .group_by(ScheduleBlock.task_id)
    ).all()
    first_blocks = {task_id: start for task_id, start in rows}
    pending = session.execute(
        select(Reminder.id, Reminder.task_id, Reminder.kind, Reminder.idempotency_key).where(
            Reminder.task_id.in_([task.id for task in tasks]), Reminder.state == "scheduled"
        )
    ).all()
    wanted: dict[uuid.UUID, str | None] = {}
    finished: set[uuid.UUID] = set()
    new_rows: list[dict[str, object]] = []
    for task in tasks:
        if task.status in FINISHED:
            finished.add(task.id)
        anchor = choose_anchor(task, first_blocks.get(task.id), now)
        if anchor is None:
            wanted[task.id] = None
            continue
        minutes = (
            task.reminder_minutes_before
            if task.reminder_minutes_before is not None
            else default_minutes
        )
        key = reminder_key(task.id, "auto", anchor.kind, anchor.at.isoformat(), minutes)
        wanted[task.id] = key
        remind_at = max(anchor.at - timedelta(minutes=minutes), now)
        new_rows.append(
            {
                "id": uuid.uuid4(),
                "user_id": user_id,
                "task_id": task.id,
                "kind": "auto",
                "anchor_kind": anchor.kind,
                "anchor_at": anchor.at,
                "remind_at": remind_at,
                "next_attempt_at": remind_at,
                "state": "scheduled",
                "attempts": 0,
                "idempotency_key": key,
            }
        )

    # Batched: replanning touches every task, so one statement per task would be too slow.
    outdated = [
        row.id
        for row in pending
        if row.task_id in finished
        or (row.kind == "auto" and row.idempotency_key != wanted.get(row.task_id))
    ]
    if outdated:
        session.execute(update(Reminder).where(Reminder.id.in_(outdated)).values(state="cancelled"))
    already_pending = {row.idempotency_key for row in pending}
    new_rows = [row for row in new_rows if row["idempotency_key"] not in already_pending]
    if new_rows:
        statement = insert(Reminder).values(new_rows)
        # A plan that moves away and back revives its cancelled reminder; delivered stays delivered.
        session.execute(
            statement.on_conflict_do_update(
                index_elements=["idempotency_key"],
                set_={
                    "state": "scheduled",
                    "attempts": 0,
                    "next_attempt_at": statement.excluded.next_attempt_at,
                },
                where=Reminder.state == "cancelled",
            )
        )
