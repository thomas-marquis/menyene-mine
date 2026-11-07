from abc import ABC, abstractmethod

from ..entities.item import Item


class ItemRepositoryPort(ABC):
    """Port interface for Item repository."""

    @abstractmethod
    async def create(self, item: Item) -> Item:
        """Create a new item."""
        ...

    @abstractmethod
    async def list_all(self) -> list[Item]:
        """List all items."""
        ...
