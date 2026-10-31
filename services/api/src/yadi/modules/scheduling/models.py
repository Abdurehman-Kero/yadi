import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from yadi.db.base import Base


class ScheduleBlock(Base):
    __tablename__ = "schedule_blocks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    task_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    reason: Mapped[str] = mapped_column(Text, default="")


class ScheduleRun(Base):
    __tablename__ = "schedule_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    unscheduled: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    conflicts: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    task_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    depends_on_task_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
