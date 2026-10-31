"""Carries out what was asked, through the same services as the app. Replies describe what happened."""

import uuid
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from yadi.core.errors import AppError
from yadi.modules.assistant.conversation import AssistantReply, ProposedAction
from yadi.modules.preferences.router import UserPreferences
from yadi.modules.scheduling import service as scheduling
from yadi.modules.scheduling.models import ScheduleBlock
from yadi.modules.scheduling.move import MoveRefused, apply_move, parse_date, parse_time, plan_move
from yadi.modules.tasks import service as tasks
from yadi.modules.tasks.lifecycle import TaskPriority
from yadi.modules.tasks.models import Task
from yadi.modules.tasks.schemas import TaskCreate, TaskUpdate

ACTOR = "ai"
ACTIVE = ("inbox", "planned", "scheduled", "in_progress")
RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
PLANNING_DAYS = 7


def _zone(session: Session, user_id: uuid.UUID) -> ZoneInfo:
    return ZoneInfo(session.get_one(UserPreferences, user_id).timezone)


def _fmt(moment: datetime, zone: ZoneInfo) -> str:
    return f"{moment.astimezone(zone):%a %d %b, %H:%M}"


def active_tasks(session: Session, user_id: uuid.UUID, limit: int) -> list[Task]:
    """Soonest first, so the most relevant tasks are the ones sent to the model."""
    rows = session.scalars(
        select(Task)
        .where(Task.user_id == user_id, Task.status.in_(ACTIVE))
        .order_by(Task.due_at.asc().nulls_last(), Task.created_at.desc(), Task.id)
        .limit(limit)
    ).all()
    return list(rows)


def _answer(message: str, *task_ids: uuid.UUID) -> AssistantReply:
    return AssistantReply(kind="answer", message=message, task_ids=list(task_ids))


def _confirm(message: str, action: ProposedAction, *task_ids: uuid.UUID) -> AssistantReply:
    return AssistantReply(kind="confirm", message=message, action=action, task_ids=list(task_ids))


def _done(message: str, *task_ids: uuid.UUID) -> AssistantReply:
    return AssistantReply(kind="done", message=message, task_ids=list(task_ids))


def _move(
    session: Session, task: Task, action: ProposedAction, *, confirmed: bool, now: datetime
) -> AssistantReply:
    zone = _zone(session, task.user_id)
    try:
        plan = plan_move(
            session,
            task,
            target_date=parse_date(action.date_local),
            period=action.period,
            target_time=parse_time(action.time_local),
            now=now,
        )
    except MoveRefused as refused:
        return _answer(str(refused), task.id)

    when = _fmt(plan.start, zone)
    if not confirmed and (task.fixed_start_at or plan.past_deadline):
        parts = [f'Move "{task.title}" to {when}?']
        if task.fixed_start_at:
            parts.append("This is a fixed commitment.")
        if plan.past_deadline and task.due_at:
            parts.append(f"That is after its deadline, {_fmt(task.due_at, zone)}.")
        if plan.clashes:
            parts.append(f"It would overlap {', '.join(plan.clashes)}.")
        return _confirm(" ".join(parts), action, task.id)
    apply_move(session, task, plan, now)
    return _done(f'Moved "{task.title}" to {when}.', task.id)


def _block_time(
    session: Session,
    user_id: uuid.UUID,
    action: ProposedAction,
    *,
    confirmed: bool,
    now: datetime,
) -> AssistantReply:
    zone = _zone(session, user_id)
    try:
        start = datetime.fromisoformat(action.start_local or "").replace(tzinfo=zone)
        end = datetime.fromisoformat(action.end_local or "").replace(tzinfo=zone)
    except ValueError:
        return _answer("From when until when are you unavailable?")
    if end <= start:
        return _answer("The end of that time must be after its start.")
    if end <= now:
        return _answer("That time has already passed.")
    if not confirmed:
        return _confirm(
            f"Block out {_fmt(start, zone)} until {end.astimezone(zone):%H:%M} and replan around "
            "it?",
            action,
        )
    task = tasks.create_task(
        session,
        user_id,
        TaskCreate(
            title="Unavailable", fixed_start_at=start, fixed_end_at=end, reminder_enabled=False
        ),
        actor=ACTOR,
    )
    schedule = scheduling.generate(session, user_id, days=PLANNING_DAYS, now=now)
    kept = sorted(
        {
            block.title
            for block in schedule.blocks
            if block.locked
            and block.task_id != task.id
            and block.start_at < end
            and start < block.end_at
        }
    )
    message = f"Blocked out {_fmt(start, zone)} until {end.astimezone(zone):%H:%M} and replanned."
    if kept:
        message += f" {', '.join(kept)} still overlaps it because you placed it there."
    return _done(message, task.id)


def _replan(session: Session, user_id: uuid.UUID, now: datetime) -> AssistantReply:
    schedule = scheduling.generate(session, user_id, days=PLANNING_DAYS, now=now)
    message = f"Replanned your next {PLANNING_DAYS} days."
    missing = len(schedule.unscheduled)
    if missing:
        names = ", ".join(item.title for item in schedule.unscheduled[:3])
        message += f" {missing} not in the plan: {names}. See Schedule for options."
    return _done(message)


def perform(
    session: Session,
    user_id: uuid.UUID,
    action: ProposedAction,
    *,
    confirmed: bool,
    now: datetime | None = None,
) -> AssistantReply:
    """Runs an action, or asks first if it is consequential. Re-checks everything every time."""
    now = now or datetime.now(UTC)
    if action.kind == "replan":
        return _replan(session, user_id, now)
    if action.kind == "block_time":
        return _block_time(session, user_id, action, confirmed=confirmed, now=now)
    if action.task_id is None:
        return _answer("Which task do you mean?")
    # Loads through the owner check: someone else's task id behaves like one that does not exist.
    task = tasks.get_task(session, user_id, action.task_id)
    title = task.title
    try:
        if action.kind == "move":
            return _move(session, task, action, confirmed=confirmed, now=now)
        if action.kind == "complete":
            tasks.complete_task(session, user_id, task.id, actor=ACTOR)
            return _done(f'Marked "{title}" as completed.', task.id)
        if action.kind == "start":
            tasks.start_task(session, user_id, task.id, actor=ACTOR)
            return _done(f'Started "{title}".', task.id)
        if action.kind == "set_priority":
            if action.priority is None:
                return _answer(f'What priority should "{title}" have?', task.id)
            data = TaskUpdate(priority=TaskPriority(action.priority))
            tasks.update_task(session, user_id, task.id, data, actor=ACTOR)
            return _done(f'"{title}" is now {action.priority} priority.', task.id)
        if not confirmed:
            return _confirm(f'Cancel "{title}"? This cannot be undone.', action, task.id)
        tasks.cancel_task(session, user_id, task.id, actor=ACTOR)
        return _done(f'Cancelled "{title}".', task.id)
    except AppError as error:
        if error.status_code != 409:
            raise
        session.rollback()
        return _answer(f'I could not change "{title}": {error.message}', task.id)


def answer_next(session: Session, user_id: uuid.UUID, now: datetime) -> AssistantReply:
    zone = _zone(session, user_id)
    row = session.execute(
        select(ScheduleBlock, Task)
        .join(Task, Task.id == ScheduleBlock.task_id)
        .where(ScheduleBlock.user_id == user_id, ScheduleBlock.end_at > now)
        .order_by(ScheduleBlock.start_at)
        .limit(1)
    ).first()
    if row:
        block, task = row
        return _answer(f'Next is "{task.title}" at {_fmt(block.start_at, zone)}.', task.id)
    active = active_tasks(session, user_id, 50)
    if not active:
        return _answer("You have nothing to do right now.")
    first = sorted(active, key=lambda t: (t.due_at is None, t.due_at or now, RANK[t.priority]))[0]
    return _answer(f'Nothing is planned yet. I would start with "{first.title}".', first.id)


def answer_free_time(
    session: Session, user_id: uuid.UUID, minutes: int | None, now: datetime
) -> AssistantReply:
    if minutes is None or minutes <= 0:
        return _answer("How much free time do you have?")
    fits = [
        t
        for t in active_tasks(session, user_id, 200)
        if t.estimated_minutes is not None
        and t.estimated_minutes <= minutes
        and t.fixed_start_at is None
    ]
    if not fits:
        return _answer(f"No task with an estimate fits in {minutes} minutes.")
    fits.sort(key=lambda t: (t.due_at is None, t.due_at or now, RANK[t.priority], t.title))
    chosen = fits[:3]
    names = "; ".join(f"{t.title} ({t.estimated_minutes} min)" for t in chosen)
    return _answer(f"In {minutes} minutes you could do: {names}.", *[t.id for t in chosen])


def answer_today(session: Session, user_id: uuid.UUID, now: datetime) -> AssistantReply:
    zone = _zone(session, user_id)
    start = now.astimezone(zone).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = session.execute(
        select(ScheduleBlock.start_at, Task.title)
        .join(Task, Task.id == ScheduleBlock.task_id)
        .where(
            ScheduleBlock.user_id == user_id,
            ScheduleBlock.end_at > now,
            ScheduleBlock.start_at < start + timedelta(days=1),
        )
        .order_by(ScheduleBlock.start_at)
    ).all()
    if not rows:
        return _answer("Nothing else is planned for today.")
    items = "; ".join(f"{moment.astimezone(zone):%H:%M} {title}" for moment, title in rows)
    return _answer(f"Still to come today: {items}.")
