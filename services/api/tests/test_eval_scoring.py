import json
from pathlib import Path
from typing import Any

from evals.scoring import score_case

from yadi.modules.assistant.schemas import ExtractedTask, Extraction


def task(title: str, **overrides: Any) -> ExtractedTask:
    values: dict[str, Any] = {
        "title": title,
        "description": None,
        "due_local": None,
        "due_phrase": None,
        "estimated_minutes": None,
        "priority": None,
        "confidence": "high",
        "questions": [],
    }
    return ExtractedTask(**{**values, **overrides})


def out(*tasks: ExtractedTask, note: str | None = None) -> Extraction:
    return Extraction(tasks=list(tasks), note=note)


CASE = {"tasks": [{"keywords": ["bank"], "due_local": "2026-11-05T09:00"}], "questions": False}
QUESTION = {"field": "due", "question": "When?"}


def test_a_correct_answer_passes() -> None:
    assert score_case(CASE, out(task("Call the Bank", due_local="2026-11-05T09:00"))) == []


def test_wrong_field_and_missing_task_fail() -> None:
    assert "due_local" in score_case(CASE, out(task("Call the bank")))[0]
    assert "missing task: bank" in score_case(CASE, out(task("Walk the dog")))


def test_questions_are_checked_both_ways() -> None:
    wrong = out(task("bank", due_local="2026-11-05T09:00", questions=[QUESTION]))
    assert "unnecessary question" in score_case(CASE, wrong)
    assert "should have asked a question" in score_case({"questions": True}, out(task("x")))


def test_count_limits_and_note() -> None:
    assert score_case({"count_max": 0, "note": True}, out(note="Only tasks.")) == []
    failures = score_case({"count_max": 0, "note": True}, out(task("x")))
    assert "too many tasks: 1" in failures and "should have explained in note" in failures


def test_the_case_file_is_valid_and_covers_every_required_kind() -> None:
    path = Path(__file__).parents[1] / "evals" / "cases.json"
    cases = json.loads(path.read_text("utf-8"))["cases"]
    assert len({case["id"] for case in cases}) == len(cases)
    kinds = {case["kind"] for case in cases}
    required = {"clear", "multi", "ambiguous", "conflicting", "misheard", "over-capacity"}
    assert required | {"unsupported"} <= kinds
