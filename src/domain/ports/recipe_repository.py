from abc import ABC, abstractmethod

from ..entities.recipe import Recipe


class RecipeRepositoryPort(ABC):
    """Port interface for Recipe repository."""

    @abstractmethod
    async def create(self, recipe: Recipe) -> Recipe:
        """Create a new recipe."""
        ...

    @abstractmethod
    async def get_by_id(self, recipe_id: int) -> Recipe | None:
        """Get a recipe by its ID."""
        ...

    @abstractmethod
    async def update(self, recipe: Recipe) -> Recipe | None:
        """Update an existing recipe."""
        ...

    @abstractmethod
    async def delete(self, recipe_id: int) -> bool:
        """Delete a recipe by its ID."""
        ...

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Recipe]:
        """List all recipes with pagination."""
        ...

    @abstractmethod
    async def search(self, keyword: str, skip: int = 0, limit: int = 100) -> list[Recipe]:
        """Search recipes by keyword in title or content."""
        ...
