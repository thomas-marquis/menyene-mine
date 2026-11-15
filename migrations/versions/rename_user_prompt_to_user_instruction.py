"""Rename user_prompt to user_instruction in recipe_drafts table

Revision ID: rename_user_prompt_to_instruction
Revises: e8f7e4d3b5a2
Create Date: 2026-11-15 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "rename_user_prompt_to_instruction"
down_revision: str | None = "e8f7e4d3b5a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Rename user_prompt column to user_instruction
    op.alter_column(
        "recipe_drafts",
        "user_prompt",
        new_column_name="user_instruction",
        nullable=False,
    )


def downgrade() -> None:
    # Rename user_instruction column back to user_prompt
    op.alter_column(
        "recipe_drafts",
        "user_instruction",
        new_column_name="user_prompt",
        nullable=False,
    )
