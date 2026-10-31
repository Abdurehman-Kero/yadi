"""Task status rules. Pure: no database, no clock."""

from enum import StrEnum


class TaskStatus(StrEnum):
    INBOX = "inbox"
    PLANNED = "planned"
    SCHEDULED = "scheduled"  # Set only by the scheduler.
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


ALLOWED_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.INBOX: frozenset(
        {
            TaskStatus.PLANNED,
            TaskStatus.SCHEDULED,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.PLANNED: frozenset(
        {
            TaskStatus.INBOX,
            TaskStatus.SCHEDULED,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.SCHEDULED: frozenset(
        {
            TaskStatus.INBOX,
            TaskStatus.PLANNED,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.IN_PROGRESS: frozenset({TaskStatus.COMPLETED, TaskStatus.CANCELLED}),
    # Reopening returns to whichever of inbox/planned the task's details justify.
    TaskStatus.COMPLETED: frozenset({TaskStatus.INBOX, TaskStatus.PLANNED}),
    TaskStatus.CANCELLED: frozenset(),
}


def can_transition(current: TaskStatus, target: TaskStatus) -> bool:
    return target in ALLOWED_TRANSITIONS[current]


def status_for_details(*, has_due: bool, has_estimate: bool, has_fixed: bool = False) -> TaskStatus:
    """A task is 'planned' once it has a fixed time, or both a deadline and a duration."""
    return TaskStatus.PLANNED if has_fixed or (has_due and has_estimate) else TaskStatus.INBOX
