"""tasks and task_events

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="inbox"),
        sa.Column("priority", sa.Text(), nullable=False, server_default="medium"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('inbox','planned','scheduled','in_progress','completed','cancelled')",
            name="ck_tasks_status",
        ),
        sa.CheckConstraint(
            "priority IN ('critical','high','medium','low')", name="ck_tasks_priority"
        ),
        sa.CheckConstraint("estimated_minutes > 0", name="ck_tasks_estimate_positive"),
        sa.CheckConstraint("char_length(title) > 0", name="ck_tasks_title_nonempty"),
    )
    # Serves the task list: one user's tasks, newest first, with a stable keyset cursor.
    op.create_index(
        "ix_tasks_user_created",
        "tasks",
        ["user_id", sa.text("created_at DESC"), sa.text("id DESC")],
    )
    op.create_table(
        "task_events",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "task_id", sa.Uuid(), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("actor", sa.Text(), nullable=False),
        sa.Column("payload", JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
        sa.CheckConstraint("actor IN ('user','ai','system')", name="ck_task_events_actor"),
    )
    op.create_index("ix_task_events_task", "task_events", ["task_id", "id"])


def downgrade() -> None:
    op.drop_table("task_events")
    op.drop_table("tasks")
