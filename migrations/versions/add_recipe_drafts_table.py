"""Add recipe_drafts table

Revision ID: e8f7e4d3b5a2
Revises: d2ab91719aa8
Create Date: 2026-11-08 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e8f7e4d3b5a2"
down_revision: str | None = "d2ab91719aa8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create recipe_drafts table
    op.create_table(
        "recipe_drafts",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_prompt", sa.String(length=1000), nullable=False),
        sa.Column("generated_content", sa.JSON(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "validated", "rejected", name="recipedraftstatus"),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
            ondelete="SET NULL",
        ),
    )
    
    # Create index on status for filtering
    op.create_index(op.f("ix_recipe_drafts_status"), "recipe_drafts", ["status"], unique=False)
    
    # Create index on recipe_id for joins
    op.create_index(op.f("ix_recipe_drafts_recipe_id"), "recipe_drafts", ["recipe_id"], unique=False)
    
    # Create index on created_at for sorting
    op.create_index(op.f("ix_recipe_drafts_created_at"), "recipe_drafts", ["created_at"], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index(op.f("ix_recipe_drafts_created_at"), table_name="recipe_drafts")
    op.drop_index(op.f("ix_recipe_drafts_recipe_id"), table_name="recipe_drafts")
    op.drop_index(op.f("ix_recipe_drafts_status"), table_name="recipe_drafts")
    
    # Drop table
    op.drop_table("recipe_drafts")
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS recipedraftstatus")
