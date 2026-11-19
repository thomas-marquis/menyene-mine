"""Add meals table for meal planning

Revision ID: add_meals_table
Revises: split_recipe_components
Create Date: 2026-11-18 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "add_meals_table"
down_revision: str | None = "split_recipe_components"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create meals table for meal planning
    op.create_table(
        "meals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("moment", sa.Enum("lunch", "dinner", name="meal_moment"), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", "moment", name="uq_meal_date_moment"),
    )


def downgrade() -> None:
    # Drop meals table
    op.drop_table("meals")
