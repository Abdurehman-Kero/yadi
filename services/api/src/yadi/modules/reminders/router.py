import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from sqlalchemy import func, select, update

from yadi.config import Settings
from yadi.core.deps import CurrentUserId, DbSession
from yadi.core.errors import AppError
from yadi.modules.reminders.models import (
    Notification,
    PushSubscription,
    Reminder,
    WorkerHeartbeat,
)
from yadi.modules.reminders.sync import reminder_key
from yadi.modules.tasks.lifecycle import TaskStatus
from yadi.modules.tasks.models import Task
from yadi.modules.tasks.schemas import ApiModel, UtcDatetime

router = APIRouter(tags=["reminders"])

# A heartbeat older than this means the worker is not running.
HEARTBEAT_LIMIT = timedelta(seconds=30)


class OutModel(ApiModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class ReminderOut(OutModel):
    id: uuid.UUID
    task_id: uuid.UUID
    kind: str
    anchor_kind: str
    anchor_at: UtcDatetime
    remind_at: UtcDatetime
    state: str
    attempts: int


class NotificationOut(OutModel):
    id: uuid.UUID
    task_id: uuid.UUID
    reminder_id: uuid.UUID
    title: str
    body: str
    created_at: UtcDatetime
    read_at: UtcDatetime | None


class NotificationList(OutModel):
    items: list[NotificationOut]
    unread: int


class SnoozeRequest(ApiModel):
    minutes: Annotated[int, Field(ge=1, le=1440)]


class SubscriptionKeys(BaseModel):
    # Named by the browser's push API, so these fields are not camelCased.
    model_config = ConfigDict(extra="forbid")

    p256dh: Annotated[str, Field(min_length=1, max_length=500)]
    auth: Annotated[str, Field(min_length=1, max_length=500)]


class SubscriptionRequest(ApiModel):
    endpoint: Annotated[str, Field(pattern=r"^https://", max_length=2000)]
    keys: SubscriptionKeys


class UnsubscribeRequest(ApiModel):
    endpoint: str


class ServiceStatus(OutModel):
    running: bool
    last_beat_at: UtcDatetime | None
    overdue_reminders: int
    push_available: bool
    push_public_key: str | None


def _load_reminder(session: DbSession, user_id: uuid.UUID, reminder_id: uuid.UUID) -> Reminder:
    reminder = session.scalars(
        select(Reminder)
        .where(Reminder.id == reminder_id, Reminder.user_id == user_id)
        .with_for_update()
    ).first()
    if reminder is None:
        raise AppError("NOT_FOUND", 404, "Reminder not found.")
    return reminder


@router.get("/reminders", response_model=list[ReminderOut])
def list_reminders(session: DbSession, user_id: CurrentUserId) -> list[Reminder]:
    """What is still to come, soonest first."""
    rows = session.scalars(
        select(Reminder)
        .where(Reminder.user_id == user_id, Reminder.state == "scheduled")
        .order_by(Reminder.remind_at)
        .limit(100)
    )
    return list(rows.all())


@router.post("/reminders/{reminder_id}/snooze", response_model=ReminderOut, status_code=201)
def snooze(
    reminder_id: uuid.UUID, data: SnoozeRequest, session: DbSession, user_id: CurrentUserId
) -> Reminder:
    now = datetime.now(UTC)
    original = _load_reminder(session, user_id, reminder_id)
    task = session.get_one(Task, original.task_id)
    if task.status in (TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value):
        raise AppError("CONFLICT", 409, "This task is already finished.")
    if original.state == "scheduled":
        original.state = "cancelled"
    remind_at = now + timedelta(minutes=data.minutes)
    fresh = Reminder(
        user_id=user_id,
        task_id=original.task_id,
        kind="snooze",
        anchor_kind=original.anchor_kind,
        anchor_at=original.anchor_at,
        remind_at=remind_at,
        next_attempt_at=remind_at,
        state="scheduled",
        attempts=0,
        idempotency_key=reminder_key(original.id, "snooze", remind_at.isoformat()),
    )
    session.add(fresh)
    session.commit()
    return fresh


@router.post("/reminders/{reminder_id}/cancel", response_model=ReminderOut)
def cancel(reminder_id: uuid.UUID, session: DbSession, user_id: CurrentUserId) -> Reminder:
    reminder = _load_reminder(session, user_id, reminder_id)
    if reminder.state != "scheduled":
        raise AppError("CONFLICT", 409, "This reminder is no longer pending.")
    reminder.state = "cancelled"
    session.commit()
    return reminder


@router.get("/notifications")
def list_notifications(session: DbSession, user_id: CurrentUserId) -> NotificationList:
    rows = session.scalars(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc(), Notification.id)
        .limit(50)
    ).all()
    unread = session.scalar(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user_id, Notification.read_at.is_(None))
    )
    return NotificationList(
        items=[NotificationOut.model_validate(row) for row in rows], unread=unread or 0
    )


@router.post("/notifications/read-all", status_code=204)
def read_all(session: DbSession, user_id: CurrentUserId) -> None:
    session.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        .values(read_at=datetime.now(UTC))
    )
    session.commit()


@router.post("/notifications/{notification_id}/read", response_model=NotificationOut)
def read_one(
    notification_id: uuid.UUID, session: DbSession, user_id: CurrentUserId
) -> Notification:
    row = session.scalars(
        select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
    ).first()
    if row is None:
        raise AppError("NOT_FOUND", 404, "Notification not found.")
    if row.read_at is None:
        row.read_at = datetime.now(UTC)
        session.commit()
    return row


@router.post("/push/subscriptions", status_code=204)
def subscribe(data: SubscriptionRequest, session: DbSession, user_id: CurrentUserId) -> None:
    existing = session.scalars(
        select(PushSubscription).where(PushSubscription.endpoint == data.endpoint)
    ).first()
    if existing is None:
        session.add(
            PushSubscription(
                user_id=user_id,
                endpoint=data.endpoint,
                p256dh=data.keys.p256dh,
                auth=data.keys.auth,
            )
        )
    else:
        # A browser belongs to whoever most recently signed in on it.
        existing.user_id = user_id
        existing.p256dh = data.keys.p256dh
        existing.auth = data.keys.auth
    session.commit()


@router.post("/push/unsubscribe", status_code=204)
def unsubscribe(data: UnsubscribeRequest, session: DbSession, user_id: CurrentUserId) -> None:
    row = session.scalars(
        select(PushSubscription).where(
            PushSubscription.endpoint == data.endpoint, PushSubscription.user_id == user_id
        )
    ).first()
    if row is not None:
        session.delete(row)
        session.commit()


@router.get("/reminders/service-status")
def service_status(request: Request, session: DbSession, user_id: CurrentUserId) -> ServiceStatus:
    settings: Settings = request.app.state.settings
    now = datetime.now(UTC)
    beat = session.get(WorkerHeartbeat, "reminders")
    overdue = session.scalar(
        select(func.count())
        .select_from(Reminder)
        .where(
            Reminder.user_id == user_id,
            Reminder.state == "scheduled",
            Reminder.next_attempt_at <= now,
        )
    )
    public_key = settings.vapid_public_key or None
    return ServiceStatus(
        running=beat is not None and now - beat.beat_at < HEARTBEAT_LIMIT,
        last_beat_at=beat.beat_at if beat else None,
        overdue_reminders=overdue or 0,
        push_available=public_key is not None,
        push_public_key=public_key,
    )
