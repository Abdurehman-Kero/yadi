"""Runs the evaluation set against the real model. Uses quota or money, so it requires --yes.

Usage, from services/api, in Git Bash on Windows:
    PYTHONPATH="src;." python -m uv run python scripts/run_ai_eval.py --yes
Add --intents to score understanding of changes and questions instead of new tasks.
"""

import json
import sys
import time
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from evals.intents import score_intent
from evals.scoring import score_case

from yadi.config import Settings
from yadi.modules.assistant.ai.client import AiError
from yadi.modules.assistant.ai.gemini_client import GeminiLlmClient
from yadi.modules.assistant.conversation import SYSTEM_PROMPT as CONVERSATION_PROMPT
from yadi.modules.assistant.conversation import Intent
from yadi.modules.assistant.conversation import build_prompt as build_message_prompt
from yadi.modules.assistant.extraction import SYSTEM_PROMPT, build_prompt
from yadi.modules.assistant.schemas import Extraction
from yadi.modules.assistant.service import estimate_cost
from yadi.modules.tasks.models import Task

# Free-tier limits are per minute; pacing keeps a run from failing on them.
PACE_SECONDS = 6.5


def _flag(name: str) -> str | None:
    for arg in sys.argv:
        if arg.startswith(f"--{name}="):
            return arg.split("=", 1)[1]
    return None


def _selected(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    only = _flag("only")
    return [c for c in cases if only is None or c["id"] in only.split(",")]


def _timed(client: GeminiLlmClient, schema: Any, system: str, prompt: str) -> Any:
    time.sleep(PACE_SECONDS)
    start = time.perf_counter()
    result = client.generate_structured(schema=schema, system=system, prompt=prompt)
    LATENCIES.append(time.perf_counter() - start)
    return result


def _report_latency() -> None:
    if LATENCIES:
        ordered = sorted(LATENCIES)
        print(f"Latency: median {ordered[len(ordered) // 2]:.1f} s, slowest {ordered[-1]:.1f} s.")


LATENCIES: list[float] = []


def _candidate(raw: dict[str, Any], number: int) -> Task:
    return Task(
        id=uuid.UUID(int=number),
        title=raw["title"],
        status=raw["status"],
        due_at=datetime.fromisoformat(raw["due"]) if "due" in raw else None,
        fixed_start_at=datetime.fromisoformat(raw["fixed_start"]) if "fixed_start" in raw else None,
    )


def run_intents(client: GeminiLlmClient) -> None:
    data = json.loads(
        (Path(__file__).parents[1] / "evals" / "intent_cases.json").read_text("utf-8")
    )
    now = datetime.fromisoformat(data["now"])
    tasks = [_candidate(raw, i) for i, raw in enumerate(data["tasks"], start=1)]
    passed = 0
    cases = _selected(data["cases"])
    for case in cases:
        prompt = build_message_prompt(
            case["text"],
            tasks=tasks,
            recent={uuid.UUID(int=n) for n in case.get("recent", [])},
            history=[],
            now=now,
            timezone=data["timezone"],
        )
        try:
            result = _timed(client, Intent, CONVERSATION_PROMPT, prompt)
        except AiError as exc:
            print(f"ERROR {case['id']}: {exc.kind}")
            continue
        failures = score_intent(case["expect"], result.output)
        passed += not failures
        print(f"{'PASS' if not failures else 'FAIL'}  {case['id']}")
        for failure in failures:
            print(f"      {failure}")
    print(f"\nIntents: {passed}/{len(cases)} passed.")
    _report_latency()


def main() -> int:
    if "--yes" not in sys.argv:
        print("This calls the Gemini API for every case. Re-run with --yes to proceed.")
        return 2
    settings = Settings()
    if not settings.gemini_api_key or not settings.gemini_api_key.get_secret_value():
        print("GEMINI_API_KEY is not set.")
        return 2

    data = json.loads((Path(__file__).parents[1] / "evals" / "cases.json").read_text("utf-8"))
    now = datetime.fromisoformat(data["now"])
    client = GeminiLlmClient(
        api_key=settings.gemini_api_key.get_secret_value(), model=settings.ai_model
    )
    if "--intents" in sys.argv:
        run_intents(client)
        return 0
    passed = 0
    cost = Decimal(0)
    cases = _selected(data["cases"])
    for case in cases:
        prompt = build_prompt(case["text"], now=now, timezone=data["timezone"])
        try:
            result = _timed(client, Extraction, SYSTEM_PROMPT, prompt)
        except AiError as exc:
            print(f"ERROR {case['id']}: {exc.kind}")
            continue
        cost += estimate_cost(result.model, result.input_tokens, result.output_tokens) or 0
        failures = score_case(case, result.output)
        passed += not failures
        print(f"{'PASS' if not failures else 'FAIL'}  {case['id']}")
        for failure in failures:
            print(f"      {failure}")
    print(f"\n{passed}/{len(cases)} passed. Model {client.model}. Estimated cost ${cost:.4f}.")
    _report_latency()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
