"""Scores one interpreted message against an evaluation case. Returns the failed checks."""

from typing import Any

from yadi.modules.assistant.conversation import Intent


def score_intent(expected: dict[str, Any], output: Intent) -> list[str]:
    failures = []
    for name, value in expected.items():
        actual = getattr(output, name)
        if name == "task_numbers":
            actual, value = sorted(actual), sorted(value)
        if actual != value:
            failures.append(f"{name} is {actual!r}, not {value!r}")
    return failures
