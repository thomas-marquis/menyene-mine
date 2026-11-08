from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.grocery_item import GroceryItem as GroceryItemEntity
from ...domain.ports.grocery_repository import GroceryRepositoryPort
from ..models.grocery_item import GroceryItem as GroceryItemModel


class GroceryRepositoryImpl(GroceryRepositoryPort):
    """SQLAlchemy implementation of GroceryItem repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, grocery_item: GroceryItemEntity) -> GroceryItemEntity:
        """Create a new grocery item in the database."""
        grocery_item_model = GroceryItemModel(
            name=grocery_item.name,
            quantity=grocery_item.quantity,
            is_completed=grocery_item.is_completed
            if grocery_item.is_completed is not None
            else False,
        )
        self.session.add(grocery_item_model)
        await self.session.commit()
        await self.session.refresh(grocery_item_model)
        return GroceryItemEntity(
            id=grocery_item_model.id,
            name=grocery_item_model.name,
            quantity=grocery_item_model.quantity,
            is_completed=grocery_item_model.is_completed,
            created_at=grocery_item_model.created_at,
            updated_at=grocery_item_model.updated_at,
        )

    async def get_by_id(self, grocery_item_id: int) -> GroceryItemEntity | None:
        """Get a grocery item by its ID."""
        result = await self.session.execute(
            select(GroceryItemModel).where(GroceryItemModel.id == grocery_item_id)
        )
        grocery_item_model = result.scalar_one_or_none()
        if grocery_item_model is None:
            return None
        return GroceryItemEntity(
            id=grocery_item_model.id,
            name=grocery_item_model.name,
            quantity=grocery_item_model.quantity,
            is_completed=grocery_item_model.is_completed,
            created_at=grocery_item_model.created_at,
            updated_at=grocery_item_model.updated_at,
        )

    async def update(self, grocery_item: GroceryItemEntity) -> GroceryItemEntity | None:
        """Update an existing grocery item."""
        result = await self.session.execute(
            select(GroceryItemModel).where(GroceryItemModel.id == grocery_item.id)
        )
        grocery_item_model = result.scalar_one_or_none()
        if grocery_item_model is None:
            return None

        if grocery_item.name is not None:
            grocery_item_model.name = grocery_item.name
        if grocery_item.quantity is not None:
            grocery_item_model.quantity = grocery_item.quantity
        if grocery_item.is_completed is not None:
            grocery_item_model.is_completed = grocery_item.is_completed
        await self.session.commit()
        await self.session.refresh(grocery_item_model)
        return GroceryItemEntity(
            id=grocery_item_model.id,
            name=grocery_item_model.name,
            quantity=grocery_item_model.quantity,
            is_completed=grocery_item_model.is_completed,
            created_at=grocery_item_model.created_at,
            updated_at=grocery_item_model.updated_at,
        )

    async def delete(self, grocery_item_id: int) -> bool:
        """Delete a grocery item by its ID."""
        result = await self.session.execute(
            select(GroceryItemModel).where(GroceryItemModel.id == grocery_item_id)
        )
        grocery_item_model = result.scalar_one_or_none()
        if grocery_item_model is None:
            return False

        await self.session.delete(grocery_item_model)
        await self.session.commit()
        return True

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[GroceryItemEntity]:
        """List all grocery items with pagination."""
        result = await self.session.execute(
            select(GroceryItemModel)
            .order_by(GroceryItemModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        grocery_items = result.scalars().all()
        return [
            GroceryItemEntity(
                id=gi.id,
                name=gi.name,
                quantity=gi.quantity,
                is_completed=gi.is_completed,
                created_at=gi.created_at,
                updated_at=gi.updated_at,
            )
            for gi in grocery_items
        ]
