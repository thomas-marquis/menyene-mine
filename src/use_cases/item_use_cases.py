from ..domain.entities.item import Item
from ..domain.ports.item_repository import ItemRepositoryPort


class ItemUseCases:
    """Use cases for Item operations."""

    def __init__(self, repository: ItemRepositoryPort) -> None:
        self.repository = repository

    async def create_item(self, name: str) -> Item:
        """Create a new item."""
        item = Item(name=name)
        return await self.repository.create(item)

    async def list_items(self) -> list[Item]:
        """List all items."""
        return await self.repository.list_all()
