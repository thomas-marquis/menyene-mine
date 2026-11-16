from ..domain.entities.recipe import Recipe
from ..domain.ports.recipe_repository import RecipeRepositoryPort


class RecipeUseCases:
    """Use cases for Recipe operations."""

    def __init__(self, repository: RecipeRepositoryPort) -> None:
        self._repository = repository

    async def create_recipe(
        self,
        title: str,
        summary: str,
        ingredients: list[str],
        instructions: list[str],
        servings: int = 4,
        prep_time: str = "0 minutes",
        cook_time: str = "0 minutes",
        difficulty: str = "Medium",
    ) -> Recipe:
        """Create a new recipe."""
        recipe = Recipe(
            title=title,
            summary=summary,
            ingredients=ingredients,
            instructions=instructions,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
            difficulty=difficulty,
        )
        return await self._repository.create(recipe)

    async def get_recipe(self, recipe_id: int) -> Recipe | None:
        """Get a recipe by its ID."""
        return await self._repository.get_by_id(recipe_id)

    async def update_recipe(
        self,
        recipe_id: int,
        title: str,
        summary: str,
        ingredients: list[str],
        instructions: list[str],
        servings: int = 4,
        prep_time: str = "0 minutes",
        cook_time: str = "0 minutes",
        difficulty: str = "Medium",
    ) -> Recipe | None:
        """Update an existing recipe."""
        existing_recipe = await self._repository.get_by_id(recipe_id)
        if existing_recipe is None:
            return None

        recipe = Recipe(
            id=recipe_id,
            title=title,
            summary=summary,
            ingredients=ingredients,
            instructions=instructions,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
            difficulty=difficulty,
            creation_date=existing_recipe.creation_date,
            last_updated=existing_recipe.last_updated,
        )
        return await self._repository.update(recipe)

    async def reorder_instructions(self, recipe_id: int, instructions: list[str]) -> Recipe | None:
        """Reorder instructions for a recipe via drag-and-drop."""
        existing_recipe = await self._repository.get_by_id(recipe_id)
        if existing_recipe is None:
            return None

        recipe = Recipe(
            id=recipe_id,
            title=existing_recipe.title,
            summary=existing_recipe.summary,
            ingredients=existing_recipe.ingredients,
            instructions=instructions,
            servings=existing_recipe.servings,
            prep_time=existing_recipe.prep_time,
            cook_time=existing_recipe.cook_time,
            difficulty=existing_recipe.difficulty,
            creation_date=existing_recipe.creation_date,
            last_updated=existing_recipe.last_updated,
        )
        return await self._repository.update(recipe)

    async def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe by its ID."""
        return await self._repository.delete(recipe_id)

    async def list_recipes(self, skip: int = 0, limit: int = 100) -> list[Recipe]:
        """List all recipes with pagination."""
        return await self._repository.list_all(skip=skip, limit=limit)

    async def search_recipes(self, keyword: str, skip: int = 0, limit: int = 100) -> list[Recipe]:
        """Search recipes by keyword."""
        return await self._repository.search(keyword=keyword, skip=skip, limit=limit)
