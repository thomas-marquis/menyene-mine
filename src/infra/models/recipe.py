from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    ingredients: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    instructions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    servings: Mapped[int] = mapped_column(Integer, nullable=False)
    prep_time: Mapped[str] = mapped_column(String(100), nullable=False)
    cook_time: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
