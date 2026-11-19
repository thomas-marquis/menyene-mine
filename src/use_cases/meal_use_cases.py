from datetime import date

from ..domain.entities.meal import Meal, MealMoment
from ..domain.ports.meal_repository import MealRepositoryPort
from ..domain.ports.recipe_repository import RecipeRepositoryPort


class MealUseCases:
    """Use cases for Meal operations."""

    def __init__(
        self,
        meal_repository: MealRepositoryPort,
        recipe_repository: RecipeRepositoryPort,
    ) -> None:
        self._meal_repository = meal_repository
        self._recipe_repository = recipe_repository

    async def create_meal(
        self,
        date: date,
        moment: MealMoment,
        recipe_id: int,
    ) -> Meal:
        """Create a new meal plan entry.

        Args:
            date: The date for the meal
            moment: The moment of the day (lunch or dinner)
            recipe_id: The ID of the recipe to assign

        Returns:
            The created Meal entity

        Raises:
            ValueError: If the recipe does not exist
            ValueError: If a meal already exists for the given date and moment
        """
        # Validate that the recipe exists
        recipe = await self._recipe_repository.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError(f"Recipe with id {recipe_id} does not exist")

        # Check if a meal already exists for this date and moment
        existing_meal = await self._meal_repository.get_by_date_and_moment(date, moment)
        if existing_meal is not None:
            raise ValueError(f"A meal already exists for {date} {moment.value}")

        meal = Meal(
            date=date,
            moment=moment,
            recipe_id=recipe_id,
        )
        return await self._meal_repository.create(meal)

    async def get_meal(self, date: date, moment: MealMoment) -> Meal | None:
        """Get a meal by its date and moment.

        Args:
            date: The date of the meal
            moment: The moment of the day (lunch or dinner)

        Returns:
            The Meal entity or None if not found
        """
        return await self._meal_repository.get_by_date_and_moment(date, moment)

    async def get_meal_by_id(self, meal_id: int) -> Meal | None:
        """Get a meal by its ID.

        Args:
            meal_id: The ID of the meal

        Returns:
            The Meal entity or None if not found
        """
        return await self._meal_repository.get_by_id(meal_id)

    async def get_meals_for_month(self, year: int, month: int) -> list[Meal]:
        """Get all meals for a specific month.

        Args:
            year: The year
            month: The month (1-12)

        Returns:
            List of Meal entities for the month
        """
        return await self._meal_repository.get_meals_for_month(year, month)

    async def update_meal(
        self,
        meal_id: int,
        recipe_id: int,
    ) -> Meal | None:
        """Update the recipe for an existing meal.

        Args:
            meal_id: The ID of the meal to update
            recipe_id: The new recipe ID

        Returns:
            The updated Meal entity or None if not found

        Raises:
            ValueError: If the recipe does not exist
        """
        # Validate that the recipe exists
        recipe = await self._recipe_repository.get_by_id(recipe_id)
        if recipe is None:
            raise ValueError(f"Recipe with id {recipe_id} does not exist")

        # Get the existing meal
        meal = await self._meal_repository.get_by_id(meal_id)
        if meal is None:
            return None

        # Update the meal with the new recipe_id
        meal.recipe_id = recipe_id
        return await self._meal_repository.update(meal)

    async def delete_meal(self, meal_id: int) -> bool:
        """Delete a meal by its ID.

        Args:
            meal_id: The ID of the meal to delete

        Returns:
            True if the meal was deleted, False otherwise
        """
        return await self._meal_repository.delete(meal_id)

    async def get_meals_by_recipe_id(self, recipe_id: int) -> list[Meal]:
        """Get all meals that reference a specific recipe.

        Args:
            recipe_id: The ID of the recipe

        Returns:
            List of Meal entities that reference the recipe
        """
        return await self._meal_repository.get_meals_by_recipe_id(recipe_id)

    async def check_recipe_has_meals(self, recipe_id: int) -> bool:
        """Check if a recipe is referenced by any meals.

        Args:
            recipe_id: The ID of the recipe

        Returns:
            True if the recipe has meals, False otherwise
        """
        meals = await self._meal_repository.get_meals_by_recipe_id(recipe_id)
        return len(meals) > 0
