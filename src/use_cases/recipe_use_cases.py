from ..domain.entities.recipe import Recipe
from ..domain.ports.recipe_repository import RecipeRepositoryPort


class RecipeUseCases:
    """Use cases for Recipe operations."""

    def __init__(self, repository: RecipeRepositoryPort) -> None:
        self.repository = repository

    async def create_recipe(self, title: str, content: str, summary: str) -> Recipe:
        """Create a new recipe."""
        recipe = Recipe(title=title, content=content, summary=summary)
        return await self.repository.create(recipe)

    async def get_recipe(self, recipe_id: int) -> Recipe | None:
        """Get a recipe by its ID."""
        return await self.repository.get_by_id(recipe_id)

    async def update_recipe(
        self, recipe_id: int, title: str, content: str, summary: str
    ) -> Recipe | None:
        """Update an existing recipe."""
        existing_recipe = await self.repository.get_by_id(recipe_id)
        if existing_recipe is None:
            return None

        recipe = Recipe(
            id=recipe_id,
            title=title,
            content=content,
            summary=summary,
            creation_date=existing_recipe.creation_date,
            last_updated=existing_recipe.last_updated,
        )
        return await self.repository.update(recipe)

    async def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe by its ID."""
        return await self.repository.delete(recipe_id)

    async def list_recipes(self, skip: int = 0, limit: int = 100) -> list[Recipe]:
        """List all recipes with pagination."""
        return await self.repository.list_all(skip=skip, limit=limit)

    async def search_recipes(self, keyword: str, skip: int = 0, limit: int = 100) -> list[Recipe]:
        """Search recipes by keyword."""
        return await self.repository.search(keyword=keyword, skip=skip, limit=limit)
