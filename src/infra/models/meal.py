from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .recipe import Recipe


class Meal(Base):
    """
    SQLAlchemy model for Meal.

    Represents a meal planned for a specific date and moment of the day.
    """

    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    moment: Mapped[str] = mapped_column(Enum("lunch", "dinner", name="meal_moment"), nullable=False)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(UTC),
        onupdate=func.now(UTC),
        nullable=False,
    )

    # Relationship to Recipe
    recipe: Mapped["Recipe"] = relationship("Recipe", backref="meals")

    __table_args__ = (
        # Unique constraint: one meal per (date, moment) combination
        UniqueConstraint("date", "moment", name="uq_meal_date_moment"),
    )
