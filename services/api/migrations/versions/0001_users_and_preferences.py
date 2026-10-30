"""users and user_preferences

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_table(
        "user_preferences",
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("timezone", sa.Text(), nullable=False, server_default="UTC"),
        sa.Column("locale", sa.Text(), nullable=False, server_default="en"),
        sa.Column("work_start", sa.Time(), nullable=False, server_default="09:00"),
        sa.Column("work_end", sa.Time(), nullable=False, server_default="17:00"),
        sa.Column("default_reminder_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("buffer_minutes", sa.Integer(), nullable=False, server_default="5"),
        sa.CheckConstraint("default_reminder_minutes >= 0", name="ck_prefs_reminder_nonneg"),
        sa.CheckConstraint("buffer_minutes >= 0", name="ck_prefs_buffer_nonneg"),
        sa.CheckConstraint("work_end > work_start", name="ck_prefs_work_hours"),
    )


def downgrade() -> None:
    op.drop_table("user_preferences")
    op.drop_table("users")
