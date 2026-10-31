import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Query

from yadi.core.deps import CurrentUserId, DbSession
from yadi.modules.tasks import service
from yadi.modules.tasks.lifecycle import TaskStatus
from yadi.modules.tasks.models import Task, TaskEvent
from yadi.modules.tasks.schemas import TaskCreate, TaskEventOut, TaskOut, TaskPage, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("")
def list_tasks(
    session: DbSession,
    user_id: CurrentUserId,
    status: Annotated[list[TaskStatus] | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: str | None = None,
) -> TaskPage:
    items, next_cursor = service.list_tasks(
        session, user_id, statuses=status or [], limit=limit, cursor=cursor
    )
    return TaskPage(items=[TaskOut.model_validate(t) for t in items], next_cursor=next_cursor)


@router.post("", status_code=201, response_model=TaskOut)
def create_task(data: TaskCreate, session: DbSession, user_id: CurrentUserId) -> Task:
    return service.create_task(session, user_id, data)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: uuid.UUID, session: DbSession, user_id: CurrentUserId) -> Task:
    return service.get_task(session, user_id, task_id)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: uuid.UUID, data: TaskUpdate, session: DbSession, user_id: CurrentUserId
) -> Task:
    return service.update_task(session, user_id, task_id, data)


@router.delete("/{task_id}", response_model=TaskOut)
def cancel_task(task_id: uuid.UUID, session: DbSession, user_id: CurrentUserId) -> Task:
    """Cancels the task. The record and its history are kept."""
    return service.cancel_task(session, user_id, task_id)


@router.post("/{task_id}/start", response_model=TaskOut)
def start_task(task_id: uuid.UUID, session: DbSession, user_id: CurrentUserId) -> Task:
    return service.start_task(session, user_id, task_id)


@router.post("/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: uuid.UUID, session: DbSession, user_id: CurrentUserId) -> Task:
    return service.complete_task(session, user_id, task_id)


@router.post("/{task_id}/reopen", response_model=TaskOut)
def reopen_task(task_id: uuid.UUID, session: DbSession, user_id: CurrentUserId) -> Task:
    return service.reopen_task(session, user_id, task_id)


@router.get("/{task_id}/events", response_model=list[TaskEventOut])
def list_events(
    task_id: uuid.UUID, session: DbSession, user_id: CurrentUserId
) -> Sequence[TaskEvent]:
    return service.list_events(session, user_id, task_id)
