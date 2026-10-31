"""Runs the evaluation set against the real model. Uses quota or money, so it requires --yes.

Usage, from services/api, in Git Bash on Windows:
    PYTHONPATH="src;." python -m uv run python scripts/run_ai_eval.py --yes
"""

import json
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from evals.scoring import score_case

from yadi.config import Settings
from yadi.modules.assistant.ai.client import AiError
from yadi.modules.assistant.ai.gemini_client import GeminiLlmClient
from yadi.modules.assistant.extraction import SYSTEM_PROMPT, build_prompt
from yadi.modules.assistant.schemas import Extraction
from yadi.modules.assistant.service import estimate_cost


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
    passed = 0
    cost = Decimal(0)
    for case in data["cases"]:
        prompt = build_prompt(case["text"], now=now, timezone=data["timezone"])
        try:
            result = client.generate_structured(
                schema=Extraction, system=SYSTEM_PROMPT, prompt=prompt
            )
        except AiError as exc:
            print(f"ERROR {case['id']}: {exc.kind}")
            continue
        cost += estimate_cost(result.model, result.input_tokens, result.output_tokens) or 0
        failures = score_case(case, result.output)
        passed += not failures
        print(f"{'PASS' if not failures else 'FAIL'}  {case['id']}")
        for failure in failures:
            print(f"      {failure}")
    print(
        f"\n{passed}/{len(data['cases'])} passed. Model {client.model}. Estimated cost ${cost:.4f}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
