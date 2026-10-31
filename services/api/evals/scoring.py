"""Scores one extraction against an evaluation case. Returns the list of failed checks."""

from typing import Any

from yadi.modules.assistant.schemas import ExtractedTask, Extraction


def _match(expected: dict[str, Any], tasks: list[ExtractedTask]) -> ExtractedTask | None:
    words = [word.lower() for word in expected.get("keywords", [])]
    for task in tasks:
        title = task.title.lower()
        if all(word in title for word in words):
            return task
    return None


def _check_task(expected: dict[str, Any], task: ExtractedTask) -> list[str]:
    name = " ".join(expected.get("keywords", []))
    failures = []
    for field in ("due_local", "estimated_minutes", "priority"):
        if field in expected and getattr(task, field) != expected[field]:
            failures.append(f"{name}: {field} is {getattr(task, field)!r}, not {expected[field]!r}")
    if "priority_in" in expected and task.priority not in expected["priority_in"]:
        failures.append(f"{name}: priority is {task.priority!r}")
    return failures


def score_case(case: dict[str, Any], output: Extraction) -> list[str]:
    failures: list[str] = []
    expected_tasks = case.get("tasks", [])
    count = len(output.tasks)
    if count < case.get("count_min", len(expected_tasks)):
        failures.append(f"too few tasks: {count}")
    if "count_max" in case and count > case["count_max"]:
        failures.append(f"too many tasks: {count}")
    for expected in expected_tasks:
        task = _match(expected, output.tasks)
        if task is None:
            failures.append(f"missing task: {' '.join(expected.get('keywords', []))}")
        else:
            failures.extend(_check_task(expected, task))

    asked = any(task.questions for task in output.tasks)
    if case.get("questions") is True and not asked:
        failures.append("should have asked a question")
    if case.get("questions") is False and asked:
        failures.append("unnecessary question")
    if case.get("note") is True and not output.note:
        failures.append("should have explained in note")
    return failures
