from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.item import Item as ItemEntity
from ...domain.ports.item_repository import ItemRepositoryPort
from ..models.item import Item as ItemModel


class ItemRepositoryImpl(ItemRepositoryPort):
    """SQLAlchemy implementation of Item repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, item: ItemEntity) -> ItemEntity:
        """Create a new item in the database."""
        item_model = ItemModel(name=item.name)
        self.session.add(item_model)
        await self.session.commit()
        await self.session.refresh(item_model)
        return ItemEntity(
            id=item_model.id,
            name=item_model.name,
            created_at=item_model.created_at,
        )

    async def list_all(self) -> list[ItemEntity]:
        """List all items from the database."""
        result = await self.session.execute(select(ItemModel).order_by(ItemModel.created_at.desc()))
        items = result.scalars().all()
        return [ItemEntity(id=item.id, name=item.name, created_at=item.created_at) for item in items]
