"""Extract task drafts: enforce the limit, call the model, record usage. Saves no tasks."""

import logging
import time
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import TypeVar
from zoneinfo import ZoneInfo

from pydantic import BaseModel
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Numeric, Text, Uuid, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from yadi.core.errors import AppError
from yadi.db.base import Base
from yadi.modules.assistant import actions
from yadi.modules.assistant.ai.client import AiError, LlmClient, LlmResult
from yadi.modules.assistant.conversation import (
    MAX_CANDIDATES,
    AssistantReply,
    Intent,
    MessageRequest,
    ProposedAction,
    TaskOption,
)
from yadi.modules.assistant.conversation import SYSTEM_PROMPT as CONVERSATION_PROMPT
from yadi.modules.assistant.conversation import build_prompt as build_message_prompt
from yadi.modules.assistant.extraction import SYSTEM_PROMPT, build_prompt, to_drafts
from yadi.modules.assistant.schemas import Extraction, ExtractResponse
from yadi.modules.preferences.router import UserPreferences
from yadi.modules.tasks.models import Task

log = logging.getLogger("yadi.assistant")
T = TypeVar("T", bound=BaseModel)

# USD per million tokens (input, output), from Google's pricing page on 2026-10-30.
# gemini-3.8-flash doubles on 2027-01-01. An unknown model records no cost estimate.
PRICES: dict[str, tuple[Decimal, Decimal]] = {
    "gemini-3.5-flash-lite": (Decimal("0.30"), Decimal("2.50")),
    "gemini-3.1-flash-lite": (Decimal("0.25"), Decimal("1.50")),
    "gemini-3.8-flash": (Decimal("0.75"), Decimal("3.75")),
}
UNAVAILABLE = "Yadi's AI is not available right now. You can add the task yourself below."


class AiUsage(Base):
    __tablename__ = "ai_usage"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    operation: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(Text)
    input_tokens: Mapped[int] = mapped_column(Integer)
    output_tokens: Mapped[int] = mapped_column(Integer)
    cost_estimate_usd: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    latency_ms: Mapped[int] = mapped_column(Integer)
    ok: Mapped[bool] = mapped_column(Boolean)
    error_kind: Mapped[str | None] = mapped_column(Text)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> Decimal | None:
    prices = PRICES.get(model)
    if prices is None:
        return None
    return (input_tokens * prices[0] + output_tokens * prices[1]) / Decimal(1_000_000)


def _check_daily_limit(session: Session, user_id: uuid.UUID, *, now: datetime, limit: int) -> None:
    used = session.scalar(
        select(func.count())
        .select_from(AiUsage)
        .where(AiUsage.user_id == user_id, AiUsage.at >= now - timedelta(days=1))
    )
    if (used or 0) >= limit:
        raise AppError(
            "RATE_LIMITED", 429, "Daily AI limit reached. You can still add tasks yourself."
        )


def call_model[T: BaseModel](
    session: Session,
    user_id: uuid.UUID,
    *,
    client: LlmClient | None,
    daily_limit: int,
    operation: str,
    schema: type[T],
    system: str,
    prompt: str,
    now: datetime,
) -> LlmResult[T]:
    """Every model call goes through here: limit, usage record, and one way of failing."""
    if client is None:
        raise AppError("AI_UNAVAILABLE", 503, UNAVAILABLE)
    _check_daily_limit(session, user_id, now=now, limit=daily_limit)
    start = time.perf_counter()
    usage = AiUsage(
        user_id=user_id,
        operation=operation,
        model=client.model,
        input_tokens=0,
        output_tokens=0,
        ok=False,
    )
    try:
        result = client.generate_structured(schema=schema, system=system, prompt=prompt)
    except AiError as exc:
        log.warning("%s failed: %s", operation, exc.kind)
        usage.error_kind = exc.kind
        usage.latency_ms = int((time.perf_counter() - start) * 1000)
        session.add(usage)
        session.commit()
        raise AppError("AI_UNAVAILABLE", 503, UNAVAILABLE) from exc

    usage.ok = True
    usage.model = result.model
    usage.input_tokens = result.input_tokens
    usage.output_tokens = result.output_tokens
    usage.cost_estimate_usd = estimate_cost(result.model, result.input_tokens, result.output_tokens)
    usage.latency_ms = int((time.perf_counter() - start) * 1000)
    session.add(usage)
    session.commit()
    return result


def extract_tasks(
    session: Session,
    user_id: uuid.UUID,
    text: str,
    *,
    client: LlmClient | None,
    daily_limit: int,
) -> ExtractResponse:
    now = datetime.now(UTC)
    if client is None:
        raise AppError("AI_UNAVAILABLE", 503, UNAVAILABLE)
    timezone = session.get_one(UserPreferences, user_id).timezone
    result = call_model(
        session,
        user_id,
        client=client,
        daily_limit=daily_limit,
        operation="extract_tasks",
        schema=Extraction,
        system=SYSTEM_PROMPT,
        prompt=build_prompt(text, now=now, timezone=timezone),
        now=now,
    )
    return ExtractResponse(
        drafts=to_drafts(result.output, now=now, timezone=timezone), note=result.output.note
    )


def _resolve_targets(intent: Intent, candidates: list[Task]) -> list[Task]:
    """Task numbers come from the model, so anything not on the list it was shown is dropped."""
    seen: set[int] = set()
    targets = []
    for number in intent.task_numbers:
        if 1 <= number <= len(candidates) and number not in seen:
            seen.add(number)
            targets.append(candidates[number - 1])
    return targets


def _option_detail(task: Task, zone: ZoneInfo) -> str:
    when = task.fixed_start_at or task.due_at
    if when is None:
        return task.status.replace("_", " ").capitalize()
    label = "At" if task.fixed_start_at else "Due"
    return f"{label} {when.astimezone(zone):%a %d %b, %H:%M}"


def handle_message(
    session: Session,
    user_id: uuid.UUID,
    data: MessageRequest,
    *,
    client: LlmClient | None,
    daily_limit: int,
) -> AssistantReply:
    now = datetime.now(UTC)
    if client is None:
        raise AppError("AI_UNAVAILABLE", 503, UNAVAILABLE)
    timezone = session.get_one(UserPreferences, user_id).timezone
    candidates = actions.active_tasks(session, user_id, MAX_CANDIDATES)
    prompt = build_message_prompt(
        data.text,
        tasks=candidates,
        recent=set(data.recent_task_ids),
        history=data.history,
        now=now,
        timezone=timezone,
    )
    intent = call_model(
        session,
        user_id,
        client=client,
        daily_limit=daily_limit,
        operation="interpret_message",
        schema=Intent,
        system=CONVERSATION_PROMPT,
        prompt=prompt,
        now=now,
    ).output

    if intent.action == "create_tasks":
        return AssistantReply(kind="create_tasks", message="Let me note that down.")
    if intent.action == "ask_next":
        return actions.answer_next(session, user_id, now)
    if intent.action == "ask_today":
        return actions.answer_today(session, user_id, now)
    if intent.action == "ask_free_time":
        return actions.answer_free_time(session, user_id, intent.minutes, now)
    if intent.action == "clarify":
        return AssistantReply(kind="answer", message=intent.question or "Could you say that again?")
    if intent.action == "unsupported":
        fallback = (
            "I cannot do that. I can record tasks, change your plan and answer questions on it."
        )
        return AssistantReply(kind="answer", message=intent.note or fallback)

    action = ProposedAction(
        kind=intent.action,
        date_local=intent.date_local,
        period=intent.period,
        time_local=intent.time_local,
        priority=intent.priority,
        start_local=intent.start_local,
        end_local=intent.end_local,
    )
    if intent.action in ("block_time", "replan"):
        return actions.perform(session, user_id, action, confirmed=False, now=now)

    targets = _resolve_targets(intent, candidates)
    if not targets:
        return AssistantReply(
            kind="answer", message="I could not find that task. Which one do you mean?"
        )
    if len(targets) > 1:
        zone = ZoneInfo(timezone)
        return AssistantReply(
            kind="choose",
            message="Which one do you mean?",
            action=action,
            options=[
                TaskOption(task_id=t.id, title=t.title, detail=_option_detail(t, zone))
                for t in targets
            ],
        )
    action.task_id = targets[0].id
    return actions.perform(session, user_id, action, confirmed=False, now=now)
