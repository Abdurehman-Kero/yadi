"""The reminder worker: `python -m yadi.worker`. Safe to run several, and safe to kill at any time.

Each reminder is claimed with a short lease. If a worker dies, the lease expires and the reminder
is picked up again. The in-app notification and the `delivered` state commit together, and the
notification is unique per reminder, so a retry can never produce a second one.
"""

import logging
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import Engine, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from yadi.config import Settings
from yadi.core.logging import configure_logging
from yadi.db.session import create_db_engine
from yadi.modules.preferences.router import UserPreferences
from yadi.modules.reminders.delivery import Message, PushChannel, build_push_channel
from yadi.modules.reminders.models import (
    Notification,
    Reminder,
    ReminderAttempt,
    WorkerHeartbeat,
)
from yadi.modules.tasks.models import Task

log = logging.getLogger("yadi.worker")

BATCH_SIZE = 20
LEASE = timedelta(seconds=60)
RETRY_DELAYS = (timedelta(seconds=30), timedelta(minutes=2), timedelta(minutes=10))
MAX_ATTEMPTS = len(RETRY_DELAYS) + 1
ACTIVE = ("inbox", "planned", "scheduled", "in_progress")

InAppWriter = Callable[[Session, Message, Reminder], None]


def write_in_app(session: Session, message: Message, reminder: Reminder) -> None:
    session.execute(
        insert(Notification)
        .values(
            id=uuid.uuid4(),
            user_id=message.user_id,
            task_id=reminder.task_id,
            reminder_id=reminder.id,
            title=message.title,
            body=message.body,
        )
        .on_conflict_do_nothing(index_elements=["reminder_id"])
    )


def recover_expired_leases(session: Session, now: datetime) -> int:
    """A worker that died mid-delivery leaves a lease behind. Retry it, or give up if spent."""
    rows = session.scalars(
        select(Reminder)
        .where(Reminder.state == "processing", Reminder.locked_until < now)
        .with_for_update(skip_locked=True)
    ).all()
    for row in rows:
        row.state = "scheduled" if row.attempts < MAX_ATTEMPTS else "failed"
        row.locked_until = None
        row.next_attempt_at = now
    session.commit()
    return len(rows)


def claim_due(session: Session, now: datetime, limit: int = BATCH_SIZE) -> list[uuid.UUID]:
    rows = session.scalars(
        select(Reminder)
        .where(Reminder.state == "scheduled", Reminder.next_attempt_at <= now)
        .order_by(Reminder.next_attempt_at)
        .limit(limit)
        .with_for_update(skip_locked=True)
    ).all()
    ids = []
    for row in rows:
        row.state = "processing"
        row.locked_until = now + LEASE
        row.attempts += 1
        ids.append(row.id)
    session.commit()
    return ids


def compose(task: Task, reminder: Reminder, timezone: str, now: datetime) -> Message:
    local = reminder.anchor_at.astimezone(ZoneInfo(timezone))
    moment = (
        f"{local:%H:%M}"
        if local.date() == now.astimezone(local.tzinfo).date()
        else (f"{local:%a %d %b, %H:%M}")
    )
    verb = "Starts" if reminder.anchor_kind == "start" else "Due"
    if now >= reminder.anchor_at:
        # After an outage it is better to say so than to drop it or pretend it is on time.
        body = f"{'Started' if reminder.anchor_kind == 'start' else 'Was due'} at {moment}. "
        body += "This reminder is late."
    else:
        body = f"{verb} at {moment}."
    title = task.title if reminder.kind == "auto" else f"Snoozed: {task.title}"
    return Message(reminder.id, reminder.user_id, title, body)


def deliver_one(
    engine: Engine,
    reminder_id: uuid.UUID,
    now: datetime,
    *,
    write: InAppWriter = write_in_app,
    push: PushChannel | None = None,
) -> str:
    with Session(engine, expire_on_commit=False) as session:
        reminder = session.get_one(Reminder, reminder_id)
        if reminder.state != "processing":
            return reminder.state  # Cancelled by a task change after it was claimed.
        task = session.get_one(Task, reminder.task_id)
        if task.status not in ACTIVE:
            reminder.state = "cancelled"
            reminder.locked_until = None
            session.commit()
            return "cancelled"
        timezone = session.get_one(UserPreferences, reminder.user_id).timezone
        message = compose(task, reminder, timezone, now)
        try:
            write(session, message, reminder)
            reminder.state = "delivered"
            reminder.locked_until = None
            session.add(ReminderAttempt(reminder_id=reminder.id, channel="in_app", outcome="ok"))
            session.commit()
        except Exception as exc:
            session.rollback()
            return _record_failure(engine, reminder_id, now, type(exc).__name__)

        if push is not None:
            outcome = push.send(session, message)
            session.add(ReminderAttempt(reminder_id=reminder.id, channel="push", outcome=outcome))
            session.commit()
    return "delivered"


def _record_failure(engine: Engine, reminder_id: uuid.UUID, now: datetime, error: str) -> str:
    log.warning("reminder delivery failed: %s", error)
    with Session(engine) as session:
        reminder = session.get_one(Reminder, reminder_id)
        reminder.locked_until = None
        if reminder.attempts >= MAX_ATTEMPTS:
            reminder.state = "failed"
        else:
            reminder.state = "scheduled"
            reminder.next_attempt_at = now + RETRY_DELAYS[reminder.attempts - 1]
        session.add(
            ReminderAttempt(
                reminder_id=reminder_id, channel="in_app", outcome="failed", error_kind=error
            )
        )
        session.commit()
        return reminder.state


def process_due(
    engine: Engine,
    now: datetime,
    *,
    write: InAppWriter = write_in_app,
    push: PushChannel | None = None,
) -> int:
    with Session(engine) as session:
        recover_expired_leases(session, now)
        claimed = claim_due(session, now)
    for reminder_id in claimed:
        deliver_one(engine, reminder_id, now, write=write, push=push)
    return len(claimed)


def beat(engine: Engine, now: datetime) -> None:
    with Session(engine) as session:
        session.execute(
            insert(WorkerHeartbeat)
            .values(name="reminders", beat_at=now)
            .on_conflict_do_update(index_elements=["name"], set_={"beat_at": now})
        )
        session.commit()


def run(settings: Settings) -> None:
    configure_logging(settings.log_level)
    engine = create_db_engine(settings)
    push = build_push_channel(settings)
    log.info("reminder worker started; push %s", "on" if push else "not configured")
    while True:
        try:
            now = datetime.now(UTC)
            beat(engine, now)
            process_due(engine, now, push=push)
        except (OperationalError, ProgrammingError) as exc:
            # A database that is down or not yet migrated is expected to pass: keep trying.
            log.warning("database not ready: %s", type(exc.orig).__name__)
        time.sleep(settings.worker_poll_seconds)


if __name__ == "__main__":
    run(Settings())
