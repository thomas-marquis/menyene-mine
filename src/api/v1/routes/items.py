from typing import Annotated

from fastapi import APIRouter, Depends

from ....db import AsyncSession, get_session
from ....schemas.items import ItemCreate, ItemResponse
from ....services.items import create_item, list_items

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/", response_model=list[ItemResponse])
async def list_items_endpoint(session: SessionDep) -> list[ItemResponse]:
    return await list_items(session)


@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item_endpoint(payload: ItemCreate, session: SessionDep) -> ItemResponse:
    return await create_item(session, payload)
