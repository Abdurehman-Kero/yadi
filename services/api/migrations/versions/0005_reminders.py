"""Durable reminders, delivery records, in-app notifications, push subscriptions, worker heartbeat.

Revision ID: 0005
Revises: 0004
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def _uuid_pk() -> sa.Column[object]:
    return sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()"))


def _uuid_fk(name: str, target: str) -> sa.Column[object]:
    return sa.Column(name, sa.Uuid(), sa.ForeignKey(target, ondelete="CASCADE"), nullable=False)


def _when(name: str, *, nullable: bool = False, now: bool = False) -> sa.Column[object]:
    default = sa.text("now()") if now else None
    return sa.Column(name, sa.DateTime(timezone=True), nullable=nullable, server_default=default)


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("reminder_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("tasks", sa.Column("reminder_minutes_before", sa.Integer(), nullable=True))
    op.create_check_constraint("ck_tasks_reminder_minutes", "tasks", "reminder_minutes_before >= 0")

    op.create_table(
        "reminders",
        _uuid_pk(),
        _uuid_fk("user_id", "users.id"),
        _uuid_fk("task_id", "tasks.id"),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("anchor_kind", sa.Text(), nullable=False),
        _when("anchor_at"),
        _when("remind_at"),
        sa.Column("state", sa.Text(), nullable=False, server_default="scheduled"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        _when("next_attempt_at"),
        _when("locked_until", nullable=True),
        sa.Column("idempotency_key", sa.Text(), nullable=False, unique=True),
        _when("created_at", now=True),
        sa.CheckConstraint(
            "state IN ('scheduled','processing','delivered','failed','cancelled')",
            name="ck_reminders_state",
        ),
        sa.CheckConstraint("kind IN ('auto','snooze')", name="ck_reminders_kind"),
        sa.CheckConstraint("anchor_kind IN ('start','due')", name="ck_reminders_anchor_kind"),
    )
    op.create_index(
        "ix_reminders_due",
        "reminders",
        ["next_attempt_at"],
        postgresql_where=sa.text("state = 'scheduled'"),
    )
    op.create_index(
        "ix_reminders_leases",
        "reminders",
        ["locked_until"],
        postgresql_where=sa.text("state = 'processing'"),
    )
    op.create_index("ix_reminders_task", "reminders", ["task_id", "state"])
    op.create_index("ix_reminders_user", "reminders", ["user_id", "remind_at"])

    op.create_table(
        "reminder_attempts",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        _uuid_fk("reminder_id", "reminders.id"),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("error_kind", sa.Text(), nullable=True),
        _when("at", now=True),
    )
    op.create_index("ix_reminder_attempts_reminder", "reminder_attempts", ["reminder_id", "id"])

    op.create_table(
        "notifications",
        _uuid_pk(),
        _uuid_fk("user_id", "users.id"),
        _uuid_fk("task_id", "tasks.id"),
        sa.Column(
            "reminder_id",
            sa.Uuid(),
            sa.ForeignKey("reminders.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        _when("created_at", now=True),
        _when("read_at", nullable=True),
    )
    op.create_index("ix_notifications_user", "notifications", ["user_id", "created_at"])

    op.create_table(
        "push_subscriptions",
        _uuid_pk(),
        _uuid_fk("user_id", "users.id"),
        sa.Column("endpoint", sa.Text(), nullable=False, unique=True),
        sa.Column("p256dh", sa.Text(), nullable=False),
        sa.Column("auth", sa.Text(), nullable=False),
        _when("created_at", now=True),
    )

    op.create_table(
        "worker_heartbeat",
        sa.Column("name", sa.Text(), primary_key=True),
        _when("beat_at"),
    )


def downgrade() -> None:
    op.drop_table("worker_heartbeat")
    op.drop_table("push_subscriptions")
    op.drop_table("notifications")
    op.drop_table("reminder_attempts")
    op.drop_table("reminders")
    op.drop_constraint("ck_tasks_reminder_minutes", "tasks")
    op.drop_column("tasks", "reminder_minutes_before")
    op.drop_column("tasks", "reminder_enabled")
