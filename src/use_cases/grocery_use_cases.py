from ..domain.entities.grocery_item import GroceryItem
from ..domain.ports.grocery_repository import GroceryRepositoryPort


class GroceryUseCases:
    """Use cases for GroceryItem operations."""

    def __init__(self, repository: GroceryRepositoryPort) -> None:
        self.repository = repository

    async def create_grocery_item(
        self, name: str, quantity: str | None = None, is_completed: bool = False
    ) -> GroceryItem:
        """Create a new grocery item."""
        grocery_item = GroceryItem(
            name=name,
            quantity=quantity,
            is_completed=is_completed,
        )
        return await self.repository.create(grocery_item)

    async def get_grocery_item(self, grocery_item_id: int) -> GroceryItem | None:
        """Get a grocery item by its ID."""
        return await self.repository.get_by_id(grocery_item_id)

    async def update_grocery_item(
        self,
        grocery_item_id: int,
        name: str | None = None,
        quantity: str | None = None,
        is_completed: bool | None = None,
    ) -> GroceryItem | None:
        """Update an existing grocery item."""
        existing_grocery_item = await self.repository.get_by_id(grocery_item_id)
        if existing_grocery_item is None:
            return None

        grocery_item = GroceryItem(
            id=grocery_item_id,
            name=name if name is not None else existing_grocery_item.name,
            quantity=quantity if quantity is not None else existing_grocery_item.quantity,
            is_completed=is_completed
            if is_completed is not None
            else existing_grocery_item.is_completed,
            created_at=existing_grocery_item.created_at,
            updated_at=existing_grocery_item.updated_at,
        )
        return await self.repository.update(grocery_item)

    async def delete_grocery_item(self, grocery_item_id: int) -> bool:
        """Delete a grocery item by its ID."""
        return await self.repository.delete(grocery_item_id)

    async def list_grocery_items(self, skip: int = 0, limit: int = 100) -> list[GroceryItem]:
        """List all grocery items with pagination."""
        return await self.repository.list_all(skip=skip, limit=limit)
