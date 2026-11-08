from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...di import get_grocery_use_cases
from ...domain.entities.grocery_item import GroceryItem
from ...use_cases.grocery_use_cases import GroceryUseCases
from .schemas import (
    GroceryItemCreate,
    GroceryItemListResponse,
    GroceryItemResponse,
    GroceryItemUpdate,
)

router = APIRouter(prefix="/groceries", tags=["groceries"])

GroceryUseCasesDep = Annotated[GroceryUseCases, Depends(get_grocery_use_cases)]


def _grocery_item_to_response(grocery_item: GroceryItem) -> GroceryItemResponse:
    """Convert domain GroceryItem entity to GroceryItemResponse schema."""
    return GroceryItemResponse(
        id=grocery_item.id,
        name=grocery_item.name,
        quantity=grocery_item.quantity,
        is_completed=grocery_item.is_completed,
        created_at=grocery_item.created_at,
        updated_at=grocery_item.updated_at,
    )


@router.post("/", response_model=GroceryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_grocery_item_endpoint(
    payload: GroceryItemCreate, use_cases: GroceryUseCasesDep
) -> GroceryItemResponse:
    """Create a new grocery item."""
    grocery_item = await use_cases.create_grocery_item(
        name=payload.name,
        quantity=payload.quantity,
        is_completed=payload.is_completed,
    )
    return _grocery_item_to_response(grocery_item)


@router.get("/", response_model=GroceryItemListResponse)
async def list_grocery_items_endpoint(
    use_cases: GroceryUseCasesDep,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
) -> GroceryItemListResponse:
    """List all grocery items with pagination."""
    grocery_items = await use_cases.list_grocery_items(skip=skip, limit=limit)
    total = len(grocery_items)
    return GroceryItemListResponse(
        grocery_items=[_grocery_item_to_response(gi) for gi in grocery_items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{grocery_item_id}", response_model=GroceryItemResponse)
async def get_grocery_item_endpoint(
    grocery_item_id: int, use_cases: GroceryUseCasesDep
) -> GroceryItemResponse:
    """Get a single grocery item by its ID."""
    grocery_item = await use_cases.get_grocery_item(grocery_item_id)
    if grocery_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grocery item with id {grocery_item_id} not found",
        )
    return _grocery_item_to_response(grocery_item)


@router.put("/{grocery_item_id}", response_model=GroceryItemResponse)
async def update_grocery_item_endpoint(
    grocery_item_id: int, payload: GroceryItemUpdate, use_cases: GroceryUseCasesDep
) -> GroceryItemResponse:
    """Update an existing grocery item."""
    grocery_item = await use_cases.update_grocery_item(
        grocery_item_id=grocery_item_id,
        name=payload.name,
        quantity=payload.quantity,
        is_completed=payload.is_completed,
    )
    if grocery_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grocery item with id {grocery_item_id} not found",
        )
    return _grocery_item_to_response(grocery_item)


@router.delete("/{grocery_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grocery_item_endpoint(grocery_item_id: int, use_cases: GroceryUseCasesDep) -> None:
    """Delete a grocery item by its ID."""
    success = await use_cases.delete_grocery_item(grocery_item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grocery item with id {grocery_item_id} not found",
        )
