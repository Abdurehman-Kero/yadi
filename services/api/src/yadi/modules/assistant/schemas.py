from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints

from yadi.modules.tasks.lifecycle import TaskPriority
from yadi.modules.tasks.schemas import ApiModel, UtcDatetime

# --- What the model must return. Kept simple so it can be expressed as a provider schema.


class ExtractedQuestion(BaseModel):
    field: Literal["title", "due", "estimate", "priority", "other"]
    question: str


class ExtractedTask(BaseModel):
    title: str
    description: str | None
    due_local: str | None  # "YYYY-MM-DDTHH:MM" in the user's timezone
    due_phrase: str | None  # The user's own words for the time
    estimated_minutes: int | None
    priority: Literal["critical", "high", "medium", "low"] | None
    confidence: Literal["high", "medium", "low"]
    questions: list[ExtractedQuestion]


class Extraction(BaseModel):
    tasks: list[ExtractedTask]
    note: str | None  # Said to the user, e.g. when the request is not something Yadi can do


# --- The public API.


class ExtractRequest(ApiModel):
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class DraftQuestion(ApiModel):
    field: str
    question: str


class TaskDraft(ApiModel):
    title: str
    description: str | None
    due_at: UtcDatetime | None
    due_phrase: str | None
    estimated_minutes: int | None
    priority: TaskPriority
    confidence: str
    questions: list[DraftQuestion]


class ExtractResponse(ApiModel):
    drafts: list[TaskDraft]
    note: str | None
