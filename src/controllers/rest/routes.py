from typing import Annotated

from fastapi import APIRouter, Depends

from ...di import get_item_use_cases
from ...domain.entities.item import Item
from ...infra.db import AsyncSession, get_session
from ...use_cases.item_use_cases import ItemUseCases
from .schemas import ItemCreate, ItemResponse

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
UseCasesDep = Annotated[ItemUseCases, Depends(get_item_use_cases)]


def _item_to_response(item: Item) -> ItemResponse:
    """Convert domain Item entity to ItemResponse schema."""
    return ItemResponse(id=str(item.id), name=item.name, created_at=item.created_at)


@router.get("/", response_model=list[ItemResponse])
async def list_items_endpoint(use_cases: UseCasesDep) -> list[ItemResponse]:
    items = await use_cases.list_items()
    return [_item_to_response(item) for item in items]


@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item_endpoint(payload: ItemCreate, use_cases: UseCasesDep) -> ItemResponse:
    item = await use_cases.create_item(payload.name)
    return _item_to_response(item)
