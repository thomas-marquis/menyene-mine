from abc import ABC, abstractmethod

from ..entities.grocery_item import GroceryItem


class GroceryRepositoryPort(ABC):
    """Port interface for GroceryItem repository."""

    @abstractmethod
    async def create(self, grocery_item: GroceryItem) -> GroceryItem:
        """Create a new grocery item."""
        ...

    @abstractmethod
    async def get_by_id(self, grocery_item_id: int) -> GroceryItem | None:
        """Get a grocery item by its ID."""
        ...

    @abstractmethod
    async def update(self, grocery_item: GroceryItem) -> GroceryItem | None:
        """Update an existing grocery item."""
        ...

    @abstractmethod
    async def delete(self, grocery_item_id: int) -> bool:
        """Delete a grocery item by its ID."""
        ...

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[GroceryItem]:
        """List all grocery items with pagination."""
        ...
