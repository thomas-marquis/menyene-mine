from datetime import date
from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...di import get_meal_use_cases
from ...domain.entities.meal import Meal, MealMoment
from ...use_cases.meal_use_cases import MealUseCases
from .schemas import MealCreate, MealListResponse, MealResponse, MealUpdate

router = APIRouter(prefix="/meals", tags=["meals"])

MealUseCasesDep = Annotated[MealUseCases, Depends(get_meal_use_cases)]


async def _get_recipe_title(
    use_cases: MealUseCases,
    recipe_id: int,
) -> str:
    """Helper to get recipe title from recipe_id."""
    recipe = await use_cases._recipe_repository.get_by_id(recipe_id)
    return recipe.title or "Unknown Recipe" if recipe else "Unknown Recipe"


def _meal_to_response(meal: Meal) -> MealResponse:
    """Convert domain Meal entity to MealResponse schema."""
    return MealResponse(
        id=cast(int, meal.id),
        date=cast(date, meal.date),
        moment=cast(MealMoment, meal.moment).value,
        recipe_id=cast(int, meal.recipe_id),
        recipe_title="",  # Will be set later
        created_at=meal.created_at,
        updated_at=meal.updated_at,
    )


@router.post("/", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
async def create_meal_endpoint(
    payload: MealCreate,
    use_cases: MealUseCasesDep,
) -> MealResponse:
    """Create a new meal plan entry.

    Args:
        payload: MealCreate schema with date, moment, and recipe_id

    Returns:
        The created meal with recipe title

    Raises:
        HTTPException 400: If the moment is invalid
        HTTPException 404: If the recipe does not exist
        HTTPException 409: If a meal already exists for the given date and moment
    """
    try:
        moment = MealMoment(payload.moment)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid moment: {payload.moment}. Must be 'lunch' or 'dinner'.",
        ) from None

    try:
        meal = await use_cases.create_meal(
            date=payload.date,
            moment=moment,
            recipe_id=payload.recipe_id,
        )
    except ValueError as e:
        error_message = str(e)
        if "does not exist" in error_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message,
            ) from e
        elif "already exists" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message,
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        ) from e

    # Get recipe title for response
    recipe_title = await _get_recipe_title(use_cases, cast(int, meal.recipe_id))

    response = _meal_to_response(meal)
    response.recipe_title = recipe_title
    return response


@router.get("/", response_model=MealListResponse)
async def list_meals_for_month_endpoint(
    use_cases: MealUseCasesDep,
    year: int = Query(..., ge=1, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
) -> MealListResponse:
    """Get all meals for a specific month.

    Args:
        year: The year
        month: The month (1-12)

    Returns:
        List of meals for the month with recipe titles
    """
    meals = await use_cases.get_meals_for_month(year, month)

    # Get recipe titles for all meals
    meals_with_titles = []
    for meal in meals:
        recipe_title = await _get_recipe_title(use_cases, cast(int, meal.recipe_id))
        response = _meal_to_response(meal)
        response.recipe_title = recipe_title
        meals_with_titles.append(response)

    return MealListResponse(
        meals=meals_with_titles,
        total=len(meals_with_titles),
        year=year,
        month=month,
    )


@router.get("/{meal_id}", response_model=MealResponse)
async def get_meal_endpoint(
    meal_id: int,
    use_cases: MealUseCasesDep,
) -> MealResponse:
    """Get a single meal by its ID.

    Args:
        meal_id: The ID of the meal

    Returns:
        The meal with recipe title

    Raises:
        HTTPException 404: If the meal is not found
    """
    meal = await use_cases.get_meal_by_id(meal_id)
    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found",
        )

    recipe_title = await _get_recipe_title(use_cases, cast(int, meal.recipe_id))

    response = _meal_to_response(meal)
    response.recipe_title = recipe_title
    return response


@router.put("/{meal_id}", response_model=MealResponse)
async def update_meal_endpoint(
    meal_id: int,
    payload: MealUpdate,
    use_cases: MealUseCasesDep,
) -> MealResponse:
    """Update the recipe for an existing meal.

    Args:
        meal_id: The ID of the meal to update
        payload: MealUpdate schema with new recipe_id

    Returns:
        The updated meal with recipe title

    Raises:
        HTTPException 404: If the meal or recipe is not found
    """
    try:
        meal = await use_cases.update_meal(
            meal_id=meal_id,
            recipe_id=payload.recipe_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found",
        )

    recipe_title = await _get_recipe_title(use_cases, cast(int, meal.recipe_id))

    response = _meal_to_response(meal)
    response.recipe_title = recipe_title
    return response


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_endpoint(
    meal_id: int,
    use_cases: MealUseCasesDep,
) -> None:
    """Delete a meal by its ID.

    Args:
        meal_id: The ID of the meal to delete

    Raises:
        HTTPException 404: If the meal is not found
    """
    success = await use_cases.delete_meal(meal_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found",
        )
