"""User preferences. The row is created with the user, so a missing row is a server fault."""

import uuid
from datetime import time
from typing import Annotated, Self
from zoneinfo import available_timezones

from fastapi import APIRouter
from pydantic import ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_camel
from sqlalchemy import Integer, Text, Time, Uuid
from sqlalchemy.orm import Mapped, Session, mapped_column

from yadi.core.deps import CurrentUserId, DbSession
from yadi.db.base import Base
from yadi.modules.tasks.schemas import ApiModel

router = APIRouter(prefix="/preferences", tags=["preferences"])
ReminderMinutes = Annotated[int, Field(ge=0, le=10080)]
BufferMinutes = Annotated[int, Field(ge=0, le=240)]


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    timezone: Mapped[str] = mapped_column(Text)
    work_start: Mapped[time] = mapped_column(Time)
    work_end: Mapped[time] = mapped_column(Time)
    default_reminder_minutes: Mapped[int] = mapped_column(Integer)
    buffer_minutes: Mapped[int] = mapped_column(Integer)


class PreferencesModel(ApiModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, extra="forbid", from_attributes=True
    )

    timezone: str
    work_start: time
    work_end: time
    default_reminder_minutes: ReminderMinutes
    buffer_minutes: BufferMinutes

    @field_validator("timezone")
    @classmethod
    def _known_timezone(cls, value: str) -> str:
        if value not in available_timezones():
            raise ValueError("Unknown timezone.")
        return value

    @model_validator(mode="after")
    def _hours_in_order(self) -> Self:
        if self.work_end <= self.work_start:
            raise ValueError("Working hours must end after they start.")
        return self


def _get(session: Session, user_id: uuid.UUID) -> UserPreferences:
    return session.get_one(UserPreferences, user_id)


@router.get("", response_model=PreferencesModel)
def get_preferences(session: DbSession, user_id: CurrentUserId) -> UserPreferences:
    return _get(session, user_id)


@router.put("", response_model=PreferencesModel)
def put_preferences(
    data: PreferencesModel, session: DbSession, user_id: CurrentUserId
) -> UserPreferences:
    prefs = _get(session, user_id)
    for field in PreferencesModel.model_fields:
        setattr(prefs, field, getattr(data, field))
    session.commit()
    return prefs
