from itertools import product

import pytest

from yadi.modules.tasks.lifecycle import (
    ALLOWED_TRANSITIONS,
    TaskStatus,
    can_transition,
    status_for_details,
)

EXPECTED = {
    ("inbox", "planned"),
    ("inbox", "scheduled"),
    ("inbox", "in_progress"),
    ("inbox", "completed"),
    ("inbox", "cancelled"),
    ("planned", "inbox"),
    ("planned", "scheduled"),
    ("planned", "in_progress"),
    ("planned", "completed"),
    ("planned", "cancelled"),
    ("scheduled", "inbox"),
    ("scheduled", "planned"),
    ("scheduled", "in_progress"),
    ("scheduled", "completed"),
    ("scheduled", "cancelled"),
    ("in_progress", "completed"),
    ("in_progress", "cancelled"),
    ("completed", "inbox"),
    ("completed", "planned"),
}


@pytest.mark.parametrize("src,dst", list(product(TaskStatus, TaskStatus)))
def test_every_status_pair(src: TaskStatus, dst: TaskStatus) -> None:
    assert can_transition(src, dst) is ((src.value, dst.value) in EXPECTED)


def test_cancelled_is_final() -> None:
    assert ALLOWED_TRANSITIONS[TaskStatus.CANCELLED] == frozenset()


def test_status_for_details() -> None:
    assert status_for_details(has_due=True, has_estimate=True) is TaskStatus.PLANNED
    assert status_for_details(has_due=True, has_estimate=False) is TaskStatus.INBOX
    assert status_for_details(has_due=False, has_estimate=True) is TaskStatus.INBOX
    assert (
        status_for_details(has_due=False, has_estimate=False, has_fixed=True) is TaskStatus.PLANNED
    )
