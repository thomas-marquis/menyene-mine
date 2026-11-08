from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RecipeDraftStatus(StrEnum):
    """Status of a recipe draft in the database."""

    DRAFT = "draft"
    VALIDATED = "validated"
    REJECTED = "rejected"


class RecipeDraft(Base):
    """SQLAlchemy model for recipe drafts."""

    __tablename__ = "recipe_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_prompt: Mapped[str] = mapped_column(String(1000), nullable=False)
    generated_content: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(RecipeDraftStatus), default=RecipeDraftStatus.DRAFT, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    recipe_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
