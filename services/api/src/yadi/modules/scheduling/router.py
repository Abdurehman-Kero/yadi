import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Query
from pydantic import AwareDatetime

from yadi.core.deps import CurrentUserId, DbSession
from yadi.modules.preferences.router import UserPreferences
from yadi.modules.scheduling import service
from yadi.modules.scheduling.schemas import (
    BlockOut,
    BlockUpdate,
    DependenciesOut,
    DependenciesUpdate,
    GenerateRequest,
    ScheduleOut,
)

router = APIRouter(tags=["schedule"])


@router.get("/schedule")
def read_schedule(
    session: DbSession,
    user_id: CurrentUserId,
    start: Annotated[AwareDatetime | None, Query(alias="from")] = None,
    end: Annotated[AwareDatetime | None, Query(alias="to")] = None,
) -> ScheduleOut:
    """Defaults to today and the next seven days in the user's timezone."""
    if start is None:
        zone = ZoneInfo(session.get_one(UserPreferences, user_id).timezone)
        today = datetime.now(UTC).astimezone(zone)
        start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    return service.read(session, user_id, start=start, end=end or start + timedelta(days=8))


@router.post("/schedule/generate")
def generate_schedule(
    data: GenerateRequest, session: DbSession, user_id: CurrentUserId
) -> ScheduleOut:
    """Replans everything that is not fixed or locked, and applies the result."""
    return service.generate(session, user_id, days=data.days, now=datetime.now(UTC))


@router.patch("/schedule/blocks/{block_id}")
def update_block(
    block_id: uuid.UUID, data: BlockUpdate, session: DbSession, user_id: CurrentUserId
) -> BlockOut:
    service.update_block(session, user_id, block_id, data)
    return service.block_out(session, user_id, block_id)


@router.get("/tasks/{task_id}/dependencies")
def get_dependencies(
    task_id: uuid.UUID, session: DbSession, user_id: CurrentUserId
) -> DependenciesOut:
    return DependenciesOut(depends_on=service.get_dependencies(session, user_id, task_id))


@router.put("/tasks/{task_id}/dependencies")
def set_dependencies(
    task_id: uuid.UUID, data: DependenciesUpdate, session: DbSession, user_id: CurrentUserId
) -> DependenciesOut:
    return DependenciesOut(
        depends_on=service.set_dependencies(session, user_id, task_id, data.depends_on)
    )
