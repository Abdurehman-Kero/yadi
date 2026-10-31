"""Task use cases. Queries are scoped by user_id; each mutation commits with its history event."""

import base64
import binascii
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete, select, tuple_
from sqlalchemy.orm import Session

from yadi.core.errors import AppError
from yadi.modules.scheduling.models import ScheduleBlock
from yadi.modules.tasks.lifecycle import (
    TaskPriority,
    TaskStatus,
    can_transition,
    status_for_details,
)
from yadi.modules.tasks.models import Task, TaskEvent
from yadi.modules.tasks.schemas import TaskCreate, TaskUpdate, check_fixed_range

FINISHED = {TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value}


def _record(session: Session, task: Task, event_type: str, payload: dict[str, Any]) -> None:
    session.add(
        TaskEvent(
            task_id=task.id, user_id=task.user_id, type=event_type, actor="user", payload=payload
        )
    )


def _details_status(task: Task) -> TaskStatus:
    return status_for_details(
        has_due=task.due_at is not None,
        has_estimate=task.estimated_minutes is not None,
        has_fixed=task.fixed_start_at is not None,
    )


def _load(session: Session, user_id: uuid.UUID, task_id: uuid.UUID, *, lock: bool = False) -> Task:
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    if lock:
        query = query.with_for_update()
    task = session.scalars(query).first()
    if task is None:
        # The same answer for "missing" and "someone else's": existence is not revealed.
        raise AppError("NOT_FOUND", 404, "Task not found.")
    return task


def create_task(session: Session, user_id: uuid.UUID, data: TaskCreate) -> Task:
    task = Task(
        id=uuid.uuid4(),
        user_id=user_id,
        title=data.title,
        description=data.description,
        priority=data.priority.value,
        due_at=data.due_at,
        estimated_minutes=data.estimated_minutes,
        fixed_start_at=data.fixed_start_at,
        fixed_end_at=data.fixed_end_at,
        preferred_period=data.preferred_period,
    )
    task.status = _details_status(task).value
    session.add(task)
    session.flush()
    _record(session, task, "created", {})
    session.commit()
    return task


def get_task(session: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    return _load(session, user_id, task_id)


def update_task(session: Session, user_id: uuid.UUID, task_id: uuid.UUID, data: TaskUpdate) -> Task:
    task = _load(session, user_id, task_id, lock=True)
    if task.status in FINISHED:
        raise AppError("CONFLICT", 409, "Finished tasks cannot be edited. Reopen it first.")

    changed = []
    for field in data.model_fields_set:
        value = getattr(data, field)
        value = value.value if isinstance(value, TaskPriority) else value
        if getattr(task, field) != value:
            setattr(task, field, value)
            changed.append(field)
    if not changed:
        session.rollback()
        return task
    try:
        check_fixed_range(task.fixed_start_at, task.fixed_end_at)
    except ValueError as exc:
        session.rollback()
        details = [{"field": "fixedEndAt", "issue": str(exc)}]
        raise AppError("VALIDATION_FAILED", 400, "Invalid request.", details) from exc

    if task.status in (TaskStatus.INBOX, TaskStatus.PLANNED):
        task.status = _details_status(task).value
    task.updated_at = datetime.now(UTC)
    _record(session, task, "updated", {"changed": sorted(changed)})
    session.commit()
    return task


def _transition(
    session: Session, user_id: uuid.UUID, task_id: uuid.UUID, target: TaskStatus, event_type: str
) -> Task:
    task = _load(session, user_id, task_id, lock=True)
    current = TaskStatus(task.status)
    if not can_transition(current, target):
        raise AppError("CONFLICT", 409, f"A {current.value} task cannot become {target.value}.")
    task.status = target.value
    task.completed_at = datetime.now(UTC) if target is TaskStatus.COMPLETED else None
    task.updated_at = datetime.now(UTC)
    if target in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
        session.execute(
            delete(ScheduleBlock).where(
                ScheduleBlock.task_id == task.id, ScheduleBlock.end_at > task.updated_at
            )
        )
    _record(session, task, event_type, {"from": current.value, "to": target.value})
    session.commit()
    return task


def start_task(session: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    return _transition(session, user_id, task_id, TaskStatus.IN_PROGRESS, "started")


def complete_task(session: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    return _transition(session, user_id, task_id, TaskStatus.COMPLETED, "completed")


def cancel_task(session: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    return _transition(session, user_id, task_id, TaskStatus.CANCELLED, "cancelled")


def reopen_task(session: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> Task:
    task = _load(session, user_id, task_id)
    if task.status != TaskStatus.COMPLETED:
        raise AppError("CONFLICT", 409, "Only completed tasks can be reopened.")
    return _transition(session, user_id, task_id, _details_status(task), "reopened")


def list_events(session: Session, user_id: uuid.UUID, task_id: uuid.UUID) -> Sequence[TaskEvent]:
    _load(session, user_id, task_id)
    query = select(TaskEvent).where(TaskEvent.task_id == task_id).order_by(TaskEvent.id)
    return session.scalars(query).all()


def _encode_cursor(task: Task) -> str:
    raw = f"{task.created_at.isoformat()}|{task.id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    try:
        created_at, task_id = base64.urlsafe_b64decode(cursor.encode()).decode().split("|")
        return datetime.fromisoformat(created_at), uuid.UUID(task_id)
    except (ValueError, binascii.Error) as exc:
        details = [{"field": "cursor", "issue": "Invalid cursor."}]
        raise AppError("VALIDATION_FAILED", 400, "Invalid request.", details) from exc


def list_tasks(
    session: Session,
    user_id: uuid.UUID,
    *,
    statuses: Sequence[TaskStatus],
    limit: int,
    cursor: str | None,
) -> tuple[Sequence[Task], str | None]:
    """Newest first. Keyset pagination: pages stay correct while tasks are being added."""
    query = select(Task).where(Task.user_id == user_id)
    if statuses:
        query = query.where(Task.status.in_([s.value for s in statuses]))
    if cursor:
        query = query.where(tuple_(Task.created_at, Task.id) < _decode_cursor(cursor))
    query = query.order_by(Task.created_at.desc(), Task.id.desc()).limit(limit + 1)
    rows = session.scalars(query).all()
    page = rows[:limit]
    next_cursor = _encode_cursor(page[-1]) if len(rows) > limit else None
    return page, next_cursor
