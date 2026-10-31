import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from yadi.db.base import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    task_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    kind: Mapped[str] = mapped_column(Text)
    anchor_kind: Mapped[str] = mapped_column(Text)
    anchor_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    state: Mapped[str] = mapped_column(Text, default="scheduled")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReminderAttempt(Base):
    __tablename__ = "reminder_attempts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    reminder_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    channel: Mapped[str] = mapped_column(Text)
    outcome: Mapped[str] = mapped_column(Text)
    error_kind: Mapped[str | None] = mapped_column(Text)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    task_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    reminder_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    endpoint: Mapped[str] = mapped_column(Text)
    p256dh: Mapped[str] = mapped_column(Text)
    auth: Mapped[str] = mapped_column(Text)


class WorkerHeartbeat(Base):
    __tablename__ = "worker_heartbeat"

    name: Mapped[str] = mapped_column(Text, primary_key=True)
    beat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
