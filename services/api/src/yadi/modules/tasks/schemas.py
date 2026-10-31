"""API models. Extra fields are rejected, so clients cannot set status or owner by accident."""

import uuid
from datetime import UTC, datetime
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel

from yadi.modules.tasks.lifecycle import TaskPriority, TaskStatus

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Description = Annotated[str, StringConstraints(max_length=5000)]
Minutes = Annotated[int, Field(ge=1, le=1440)]
# Responses always use UTC, whatever offset the client or database session used.
PreferredPeriod = Literal["morning", "afternoon", "evening"]
UtcDatetime = Annotated[datetime, AfterValidator(lambda value: value.astimezone(UTC))]


def check_fixed_range(start: datetime | None, end: datetime | None) -> None:
    if (start is None) != (end is None):
        raise ValueError("A fixed time needs both a start and an end.")
    if start is not None and end is not None and end <= start:
        raise ValueError("A fixed time must end after it starts.")


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")


class TaskCreate(ApiModel):
    title: Title
    description: Description | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_at: AwareDatetime | None = None
    estimated_minutes: Minutes | None = None
    fixed_start_at: AwareDatetime | None = None
    fixed_end_at: AwareDatetime | None = None
    preferred_period: PreferredPeriod | None = None

    @model_validator(mode="after")
    def _fixed_range(self) -> Self:
        check_fixed_range(self.fixed_start_at, self.fixed_end_at)
        return self


class TaskUpdate(ApiModel):
    """Only the fields present in the request change; null clears the optional ones."""

    title: Title | None = None
    description: Description | None = None
    priority: TaskPriority | None = None
    due_at: AwareDatetime | None = None
    estimated_minutes: Minutes | None = None
    fixed_start_at: AwareDatetime | None = None
    fixed_end_at: AwareDatetime | None = None
    preferred_period: PreferredPeriod | None = None

    @field_validator("title", "priority")
    @classmethod
    def _not_null(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("cannot be null")
        return value


class TaskOut(ApiModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_at: UtcDatetime | None
    estimated_minutes: int | None
    fixed_start_at: UtcDatetime | None
    fixed_end_at: UtcDatetime | None
    preferred_period: PreferredPeriod | None
    completed_at: UtcDatetime | None
    created_at: UtcDatetime
    updated_at: UtcDatetime


class TaskPage(ApiModel):
    items: list[TaskOut]
    next_cursor: str | None


class TaskEventOut(ApiModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

    id: int
    type: str
    actor: str
    payload: dict[str, Any]
    at: UtcDatetime
