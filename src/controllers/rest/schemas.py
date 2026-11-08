from datetime import datetime
from typing import Annotated, Any

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


# Recipe Draft Schemas
class RecipeDraftGenerateRequest(BaseModel):
    """Request schema for generating recipe drafts."""

    prompt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
    max_drafts: int = 10


class RecipeDraftResponse(BaseModel):
    """Response schema for a recipe draft."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_prompt: str
    generated_content: dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
    recipe_id: int | None


class RecipeDraftListResponse(BaseModel):
    """Response schema for listing recipe drafts."""

    model_config = ConfigDict(from_attributes=True)

    drafts: list[RecipeDraftResponse]
    total: int
    skip: int
    limit: int


class RecipeDraftStatsResponse(BaseModel):
    """Response schema for recipe draft statistics."""

    total: int
    draft: int
    validated: int
    rejected: int


class RecipeDraftActionResponse(BaseModel):
    """Response schema for draft validation/rejection actions."""

    success: bool
    message: str
    draft: RecipeDraftResponse | None = None
    recipe: RecipeResponse | None = None
