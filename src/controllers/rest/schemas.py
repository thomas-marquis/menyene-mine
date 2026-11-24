from datetime import date, datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, StringConstraints


class RecipeCreate(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    summary: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    ingredients: list[str]
    instructions: list[str]
    servings: int = 4
    prep_time: str = "0 minutes"
    cook_time: str = "0 minutes"
    difficulty: str = "Medium"


class RecipeUpdate(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    summary: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    ingredients: list[str]
    instructions: list[str]
    servings: int = 4
    prep_time: str = "0 minutes"
    cook_time: str = "0 minutes"
    difficulty: str = "Medium"


class RecipeInstructionsReorder(BaseModel):
    """Schema for reordering recipe instructions via drag-and-drop."""

    instructions: list[str]


class RecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    creation_date: datetime
    last_updated: datetime
    summary: str
    ingredients: list[str]
    instructions: list[str]
    servings: int
    prep_time: str
    cook_time: str
    difficulty: str


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

    instruction: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
    max_drafts: int = 10
    include_meal_context: bool = True


class RecipeDraftResponse(BaseModel):
    """Response schema for a recipe draft."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_instruction: str
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


class RecipeStatsResponse(BaseModel):
    """Statistics for recipes."""

    model_config = ConfigDict(from_attributes=True)

    total_count: int


class DraftStatsResponse(BaseModel):
    """Statistics for recipe drafts by status."""

    model_config = ConfigDict(from_attributes=True)

    total_count: int
    draft_count: int
    validated_count: int
    rejected_count: int


class GroceryStatsResponse(BaseModel):
    """Statistics for grocery items."""

    model_config = ConfigDict(from_attributes=True)

    total_count: int
    active_count: int
    completed_count: int


class StatsResponse(BaseModel):
    """Response schema for all resource statistics."""

    model_config = ConfigDict(from_attributes=True)

    recipes: RecipeStatsResponse
    drafts: DraftStatsResponse
    groceries: GroceryStatsResponse


# Meal Schemas
class MealCreate(BaseModel):
    """Request schema for creating a meal."""

    date: date
    moment: Annotated[str, StringConstraints(strip_whitespace=True)]  # "lunch" or "dinner"
    recipe_id: int


class MealUpdate(BaseModel):
    """Request schema for updating a meal (only recipe_id can be updated)."""

    recipe_id: int


class MealResponse(BaseModel):
    """Response schema for a meal."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    moment: str
    recipe_id: int
    recipe_title: str
    created_at: datetime
    updated_at: datetime


class MealListResponse(BaseModel):
    """Response schema for listing meals."""

    model_config = ConfigDict(from_attributes=True)

    meals: list[MealResponse]
    total: int
    year: int
    month: int
