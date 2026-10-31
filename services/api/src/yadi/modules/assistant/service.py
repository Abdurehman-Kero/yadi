"""Extract task drafts: enforce the limit, call the model, record usage. Saves no tasks."""

import logging
import time
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Numeric, Text, Uuid, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from yadi.core.errors import AppError
from yadi.db.base import Base
from yadi.modules.assistant.ai.client import AiError, LlmClient
from yadi.modules.assistant.extraction import SYSTEM_PROMPT, build_prompt, to_drafts
from yadi.modules.assistant.schemas import Extraction, ExtractResponse
from yadi.modules.preferences.router import UserPreferences

log = logging.getLogger("yadi.assistant")

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


def extract_tasks(
    session: Session,
    user_id: uuid.UUID,
    text: str,
    *,
    client: LlmClient | None,
    daily_limit: int,
) -> ExtractResponse:
    if client is None:
        raise AppError("AI_UNAVAILABLE", 503, UNAVAILABLE)
    now = datetime.now(UTC)
    _check_daily_limit(session, user_id, now=now, limit=daily_limit)
    timezone = session.get_one(UserPreferences, user_id).timezone

    start = time.perf_counter()
    usage = AiUsage(
        user_id=user_id,
        operation="extract_tasks",
        model=client.model,
        input_tokens=0,
        output_tokens=0,
        ok=False,
    )
    try:
        result = client.generate_structured(
            schema=Extraction,
            system=SYSTEM_PROMPT,
            prompt=build_prompt(text, now=now, timezone=timezone),
        )
    except AiError as exc:
        log.warning("extraction failed: %s", exc.kind)
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

    return ExtractResponse(
        drafts=to_drafts(result.output, now=now, timezone=timezone), note=result.output.note
    )
