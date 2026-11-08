from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...di import get_recipe_use_cases
from ...domain.entities.recipe import Recipe
from ...use_cases.recipe_use_cases import RecipeUseCases
from .schemas import (
    RecipeCreate,
    RecipeListResponse,
    RecipeResponse,
    RecipeUpdate,
)

router = APIRouter(prefix="/recipes", tags=["recipes"])

RecipeUseCasesDep = Annotated[RecipeUseCases, Depends(get_recipe_use_cases)]


def _recipe_to_response(recipe: Recipe) -> RecipeResponse:
    """Convert domain Recipe entity to RecipeResponse schema."""
    return RecipeResponse(
        id=recipe.id,
        title=recipe.title,
        creation_date=recipe.creation_date,
        last_updated=recipe.last_updated,
        content=recipe.content,
        summary=recipe.summary,
    )


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe_endpoint(
    payload: RecipeCreate, use_cases: RecipeUseCasesDep
) -> RecipeResponse:
    """Create a new recipe."""
    recipe = await use_cases.create_recipe(
        title=payload.title,
        content=payload.content,
        summary=payload.summary,
    )
    return _recipe_to_response(recipe)


@router.get("/", response_model=RecipeListResponse)
async def list_recipes_endpoint(
    use_cases: RecipeUseCasesDep,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
) -> RecipeListResponse:
    """List all recipes with pagination."""
    recipes = await use_cases.list_recipes(skip=skip, limit=limit)
    total = len(recipes)
    return RecipeListResponse(
        recipes=[_recipe_to_response(r) for r in recipes],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/search", response_model=RecipeListResponse)
async def search_recipes_endpoint(
    use_cases: RecipeUseCasesDep,
    keyword: str = Query(..., min_length=1, description="Search keyword"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
) -> RecipeListResponse:
    """Search recipes by keyword in title or content."""
    recipes = await use_cases.search_recipes(keyword=keyword, skip=skip, limit=limit)
    total = len(recipes)
    return RecipeListResponse(
        recipes=[_recipe_to_response(r) for r in recipes],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_endpoint(recipe_id: int, use_cases: RecipeUseCasesDep) -> RecipeResponse:
    """Get a single recipe by its ID."""
    recipe = await use_cases.get_recipe(recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found",
        )
    return _recipe_to_response(recipe)


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe_endpoint(
    recipe_id: int, payload: RecipeUpdate, use_cases: RecipeUseCasesDep
) -> RecipeResponse:
    """Update an existing recipe."""
    recipe = await use_cases.update_recipe(
        recipe_id=recipe_id,
        title=payload.title,
        content=payload.content,
        summary=payload.summary,
    )
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found",
        )
    return _recipe_to_response(recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe_endpoint(recipe_id: int, use_cases: RecipeUseCasesDep) -> None:
    """Delete a recipe by its ID."""
    success = await use_cases.delete_recipe(recipe_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found",
        )
