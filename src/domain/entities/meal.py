from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class MealMoment(Enum):
    """Enum for meal moments of the day."""

    LUNCH = "lunch"
    DINNER = "dinner"


@dataclass
class Meal:
    """
    Meal domain entity.

    Represents a meal planned for a specific date and moment of the day,
    associated with a recipe from the catalog.
    This is a pure domain object with no external dependencies.
    """

    id: int | None = None
    date: date | None = None
    moment: MealMoment | None = None
    recipe_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
