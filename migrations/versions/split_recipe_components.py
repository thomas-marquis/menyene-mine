"""Split recipe components into structured fields

Revision ID: split_recipe_components_001
Revises: e8f7e4d3b5a2
Create Date: 2026-11-15 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "split_recipe_components"
down_revision: str | None = "rename_user_prompt_to_instruction"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add new structured fields to recipes table
    op.add_column("recipes", sa.Column("ingredients", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("recipes", sa.Column("instructions", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("recipes", sa.Column("servings", sa.Integer(), nullable=False, server_default="4"))
    op.add_column("recipes", sa.Column("prep_time", sa.String(length=100), nullable=False, server_default="0 minutes"))
    op.add_column("recipes", sa.Column("cook_time", sa.String(length=100), nullable=False, server_default="0 minutes"))
    op.add_column("recipes", sa.Column("difficulty", sa.String(length=50), nullable=False, server_default="Medium"))

    # Remove the old content field
    op.drop_column("recipes", "content")


def downgrade() -> None:
    # Add back the content field
    op.add_column("recipes", sa.Column("content", sa.Text(), nullable=False, server_default=""))

    # Remove the new structured fields
    op.drop_column("recipes", "difficulty")
    op.drop_column("recipes", "cook_time")
    op.drop_column("recipes", "prep_time")
    op.drop_column("recipes", "servings")
    op.drop_column("recipes", "instructions")
    op.drop_column("recipes", "ingredients")
