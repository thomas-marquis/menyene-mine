from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class RecipeCreate(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    summary: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class RecipeUpdate(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    summary: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class RecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    creation_date: datetime
    last_updated: datetime
    content: str
    summary: str


class RecipeListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recipes: list[RecipeResponse]
    total: int
    skip: int
    limit: int


class GroceryItemCreate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    quantity: Annotated[str | None, StringConstraints(strip_whitespace=True, max_length=255)] = None
    is_completed: bool = False


class GroceryItemUpdate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    quantity: Annotated[str | None, StringConstraints(strip_whitespace=True, max_length=255)] = None
    is_completed: bool = False


class GroceryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    quantity: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime


class GroceryItemListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    grocery_items: list[GroceryItemResponse]
    total: int
    skip: int
    limit: int
