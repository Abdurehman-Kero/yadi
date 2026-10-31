import uuid
from typing import Annotated

from pydantic import AwareDatetime, ConfigDict, Field
from pydantic.alias_generators import to_camel

from yadi.modules.tasks.lifecycle import TaskPriority, TaskStatus
from yadi.modules.tasks.schemas import ApiModel, UtcDatetime


class GenerateRequest(ApiModel):
    days: Annotated[int, Field(ge=1, le=14)] = 7


class BlockUpdate(ApiModel):
    start_at: AwareDatetime
    end_at: AwareDatetime


class BlockOut(ApiModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: uuid.UUID
    task_id: uuid.UUID
    title: str
    priority: TaskPriority
    status: TaskStatus
    start_at: UtcDatetime
    end_at: UtcDatetime
    is_fixed: bool
    locked: bool
    reason: str


class UnscheduledOut(ApiModel):
    task_id: uuid.UUID
    title: str
    reason: str
    detail: str
    alternatives: list[str]


class ConflictOut(ApiModel):
    first_title: str
    second_title: str
    start_at: UtcDatetime
    end_at: UtcDatetime


class ScheduleOut(ApiModel):
    blocks: list[BlockOut]
    unscheduled: list[UnscheduledOut]
    conflicts: list[ConflictOut]
    generated_at: UtcDatetime | None
    stale: bool


class DependenciesUpdate(ApiModel):
    depends_on: list[uuid.UUID]


class DependenciesOut(ApiModel):
    depends_on: list[uuid.UUID]
