from ..db import AsyncSession
from ..repositories import items as items_repository
from ..schemas.items import ItemCreate, ItemResponse


async def create_item(session: AsyncSession, payload: ItemCreate) -> ItemResponse:
    return await items_repository.create_item(session, name=payload.name)


async def list_items(session: AsyncSession) -> list[ItemResponse]:
    return await items_repository.list_items(session)
