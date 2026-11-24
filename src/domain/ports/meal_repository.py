from abc import ABC, abstractmethod
from datetime import date

from ..entities.meal import Meal, MealMoment


class MealRepositoryPort(ABC):
    """Port interface for Meal repository."""

    @abstractmethod
    async def create(self, meal: Meal) -> Meal:
        """Create a new meal plan entry."""
        ...

    @abstractmethod
    async def get_by_id(self, meal_id: int) -> Meal | None:
        """Get a meal by its ID."""
        ...

    @abstractmethod
    async def get_by_date_and_moment(self, date: date, moment: MealMoment) -> Meal | None:
        """Get a meal by its date and moment."""
        ...

    @abstractmethod
    async def get_meals_for_month(self, year: int, month: int) -> list[Meal]:
        """Get all meals for a specific month."""
        ...

    @abstractmethod
    async def get_meals_for_date_range(
        self, start_date: date, end_date: date, unique_recipes: bool = False
    ) -> list[Meal]:
        """Get all meals within a specific date range.

        Args:
            start_date: The start date of the range (inclusive)
            end_date: The end date of the range (inclusive)
            unique_recipes: If True, return only one meal per unique recipe_id
        """
        ...

    @abstractmethod
    async def update(self, meal: Meal) -> Meal | None:
        """Update an existing meal."""
        ...

    @abstractmethod
    async def delete(self, meal_id: int) -> bool:
        """Delete a meal by its ID."""
        ...

    @abstractmethod
    async def get_meals_by_recipe_id(self, recipe_id: int) -> list[Meal]:
        """Get all meals that reference a specific recipe."""
        ...
