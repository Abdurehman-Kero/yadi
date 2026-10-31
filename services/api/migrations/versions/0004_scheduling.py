"""Fixed times and preferred period on tasks; dependencies; schedule blocks and runs.

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def _uuid_fk(name: str, target: str) -> sa.Column[object]:
    return sa.Column(name, sa.Uuid(), sa.ForeignKey(target, ondelete="CASCADE"), nullable=False)


def upgrade() -> None:
    op.add_column("tasks", sa.Column("fixed_start_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("fixed_end_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("preferred_period", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_tasks_fixed_range",
        "tasks",
        "(fixed_start_at IS NULL AND fixed_end_at IS NULL) OR fixed_end_at > fixed_start_at",
    )
    op.create_check_constraint(
        "ck_tasks_preferred_period",
        "tasks",
        "preferred_period IN ('morning','afternoon','evening')",
    )

    op.create_table(
        "task_dependencies",
        _uuid_fk("task_id", "tasks.id"),
        _uuid_fk("depends_on_task_id", "tasks.id"),
        sa.PrimaryKeyConstraint("task_id", "depends_on_task_id"),
        sa.CheckConstraint("task_id <> depends_on_task_id", name="ck_task_dependency_not_self"),
    )

    op.create_table(
        "schedule_runs",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        _uuid_fk("user_id", "users.id"),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("unscheduled", JSONB(), nullable=False, server_default="[]"),
        sa.Column("conflicts", JSONB(), nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_schedule_runs_user_created", "schedule_runs", ["user_id", "created_at"])

    op.create_table(
        "schedule_blocks",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        _uuid_fk("user_id", "users.id"),
        _uuid_fk("task_id", "tasks.id"),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_fixed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("locked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reason", sa.Text(), nullable=False, server_default=""),
        sa.CheckConstraint("end_at > start_at", name="ck_schedule_blocks_range"),
    )
    op.create_index("ix_schedule_blocks_user_start", "schedule_blocks", ["user_id", "start_at"])
    op.create_index("ix_schedule_blocks_task", "schedule_blocks", ["task_id"])


def downgrade() -> None:
    op.drop_table("schedule_blocks")
    op.drop_table("schedule_runs")
    op.drop_table("task_dependencies")
    op.drop_constraint("ck_tasks_preferred_period", "tasks")
    op.drop_constraint("ck_tasks_fixed_range", "tasks")
    op.drop_column("tasks", "preferred_period")
    op.drop_column("tasks", "fixed_end_at")
    op.drop_column("tasks", "fixed_start_at")
