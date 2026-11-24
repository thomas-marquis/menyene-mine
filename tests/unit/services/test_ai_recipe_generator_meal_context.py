"""
Unit tests for AI Recipe Generator with Meal History Context.

Tests the augmented generation feature (Task 004) that injects past meal history
into the recipe generation context.
"""

from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.entities.meal import Meal, MealMoment
from src.domain.entities.recipe import Recipe
from src.services.ai_recipe_generator import RecipeAIGenerator


@pytest.fixture
def mock_llm() -> MagicMock:
    """Create a mock LLM instance."""
    mock = MagicMock()
    mock.with_structured_output.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_meal_repository() -> AsyncMock:
    """Create a mock meal repository."""
    return AsyncMock()


@pytest.fixture
def mock_recipe_repository() -> AsyncMock:
    """Create a mock recipe repository."""
    return AsyncMock()


@pytest.fixture
def mock_recipe() -> Recipe:
    """Create a sample recipe."""
    return Recipe(
        id=1,
        title="Spaghetti Carbonara",
        summary="Classic Italian pasta with eggs, cheese, and pancetta",
        ingredients=["spaghetti", "eggs", "pecorino", "pancetta"],
        instructions=["Cook pasta", "Mix ingredients"],
        servings=4,
        prep_time="10 min",
        cook_time="15 min",
        difficulty="medium",
    )


@pytest.fixture
def mock_meal(mock_recipe: Recipe) -> Meal:
    """Create a sample meal."""
    return Meal(
        id=1,
        date=date(2026, 11, 15),
        moment=MealMoment.DINNER,
        recipe_id=mock_recipe.id,
        created_at=datetime(2026, 11, 15, 12, 0),
        updated_at=datetime(2026, 11, 15, 12, 0),
    )


@pytest.mark.asyncio
async def test_get_recent_meals_empty_history(
    mock_llm: MagicMock, mock_meal_repository: AsyncMock, mock_recipe_repository: AsyncMock
) -> None:
    """
    Given: Repositories return no meals
    When: _get_recent_meals is called
    Then: Returns empty list
    """
    # Given
    mock_meal_repository.get_meals_for_date_range.return_value = []

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # When
    meals = await generator._get_recent_meals(days=7)

    # Then
    assert meals == []


@pytest.mark.asyncio
async def test_get_recent_meals_no_meals(
    mock_llm: MagicMock, mock_meal_repository: AsyncMock, mock_recipe_repository: AsyncMock
) -> None:
    """
    Given: No meals in the past 7 days
    When: _get_recent_meals is called
    Then: Returns empty list
    """
    # Given
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    mock_meal_repository.get_meals_for_date_range.return_value = []

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # When
    meals = await generator._get_recent_meals(days=7)

    # Then
    assert meals == []
    mock_meal_repository.get_meals_for_date_range.assert_called_once_with(start_date, end_date, unique_recipes=True)


@pytest.mark.asyncio
async def test_get_recent_meals_with_meals(
    mock_llm: MagicMock,
    mock_meal_repository: AsyncMock,
    mock_recipe_repository: AsyncMock,
    mock_recipe: Recipe,
) -> None:
    """
    Given: Multiple meals in the past 7 days
    When: _get_recent_meals is called
    Then: Returns list of Recipe entities
    """
    # Given
    meal_1 = Meal(
        id=1,
        date=date(2026, 11, 20),
        moment=MealMoment.DINNER,
        recipe_id=1,
    )

    meal_2 = Meal(
        id=2,
        date=date(2026, 11, 19),
        moment=MealMoment.LUNCH,
        recipe_id=2,
    )

    mock_meal_repository.get_meals_for_date_range.return_value = [meal_1, meal_2]
    salmon_recipe = Recipe(id=2, title="Grilled Salmon", summary="Fresh salmon with lemon and herbs")
    mock_recipe_repository.get_by_id = AsyncMock(
        side_effect=lambda recipe_id: mock_recipe if recipe_id == 1 else salmon_recipe
    )

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # When
    meals = await generator._get_recent_meals(days=7)

    # Then
    assert len(meals) == 2
    assert meals[0].title == "Spaghetti Carbonara"
    assert meals[1].title == "Grilled Salmon"


@pytest.mark.asyncio
async def test_get_recent_meals_reverse_chronological(
    mock_llm: MagicMock, mock_meal_repository: AsyncMock, mock_recipe_repository: AsyncMock
) -> None:
    """
    Given: Meals on different dates
    When: _get_recent_meals is called
    Then: Meals are ordered from newest to oldest
    """
    # Given
    older_meal = Meal(
        id=1,
        date=date(2026, 11, 15),
        moment=MealMoment.DINNER,
        recipe_id=1,
    )

    newer_meal = Meal(
        id=2,
        date=date(2026, 11, 20),
        moment=MealMoment.DINNER,
        recipe_id=2,
    )

    # Repository returns meals sorted by date descending (newest first)
    mock_meal_repository.get_meals_for_date_range.return_value = [newer_meal, older_meal]
    mock_recipe_repository.get_by_id = AsyncMock(
        side_effect=lambda recipe_id: Recipe(id=recipe_id, title=f"Recipe {recipe_id}", summary=f"summary {recipe_id}")
    )

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # When
    meals = await generator._get_recent_meals(days=7)

    # Then
    assert len(meals) == 2
    # Newer meal should be first
    assert meals[0].title == "Recipe 2"
    assert meals[1].title == "Recipe 1"


@pytest.mark.asyncio
async def test_get_recent_meals_skips_meals_without_recipe_id(
    mock_llm: MagicMock, mock_meal_repository: AsyncMock, mock_recipe_repository: AsyncMock
) -> None:
    """
    Given: Mix of meals with and without recipe_id
    When: _get_recent_meals is called
    Then: Only meals with recipe_id are included
    """
    # Given
    valid_meal = Meal(
        id=1,
        date=date(2026, 11, 20),
        moment=MealMoment.DINNER,
        recipe_id=1,
    )

    invalid_meal = Meal(
        id=2,
        date=date(2026, 11, 19),
        moment=MealMoment.LUNCH,
        recipe_id=None,
    )

    mock_meal_repository.get_meals_for_date_range.return_value = [valid_meal, invalid_meal]
    mock_recipe_repository.get_by_id = AsyncMock(return_value=Recipe(id=1, title="Valid Recipe", summary="valid"))

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # When
    meals = await generator._get_recent_meals(days=7)

    # Then
    assert len(meals) == 1
    assert meals[0].title == "Valid Recipe"


@pytest.mark.asyncio
async def test_get_recent_meals_skips_duplicate_recipes(
    mock_llm: MagicMock, mock_meal_repository: AsyncMock, mock_recipe_repository: AsyncMock
) -> None:
    """
    Given: Multiple meals referencing the same recipe
    When: _get_recent_meals is called
    Then: Each recipe appears only once
    """
    # Given
    meal_1 = Meal(
        id=1,
        date=date(2026, 11, 20),
        moment=MealMoment.DINNER,
        recipe_id=1,
    )

    meal_2 = Meal(
        id=2,
        date=date(2026, 11, 19),
        moment=MealMoment.LUNCH,
        recipe_id=1,  # Same recipe_id
    )

    # Mock repository to return only one meal when unique_recipes=True
    async def get_meals_side_effect(start_date: date, end_date: date, unique_recipes: bool = False) -> list[Meal]:
        if unique_recipes:
            return [meal_1]  # Only return one meal per recipe
        return [meal_1, meal_2]

    mock_meal_repository.get_meals_for_date_range = AsyncMock(side_effect=get_meals_side_effect)
    mock_recipe_repository.get_by_id = AsyncMock(
        return_value=Recipe(id=1, title="Duplicate Recipe", summary="duplicate")
    )

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # When
    meals = await generator._get_recent_meals(days=7)

    # Then
    assert len(meals) == 1
    assert meals[0].title == "Duplicate Recipe"


@pytest.mark.asyncio
async def test_get_recent_meals_handles_missing_recipes(
    mock_llm: MagicMock, mock_meal_repository: AsyncMock, mock_recipe_repository: AsyncMock
) -> None:
    """
    Given: Meal references a recipe that doesn't exist
    When: _get_recent_meals is called
    Then: Missing recipe is skipped gracefully
    """
    # Given
    meal = Meal(
        id=1,
        date=date(2026, 11, 20),
        moment=MealMoment.DINNER,
        recipe_id=999,  # Non-existent recipe
    )

    mock_meal_repository.get_meals_for_date_range.return_value = [meal]
    mock_recipe_repository.get_by_id = AsyncMock(return_value=None)

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # When
    meals = await generator._get_recent_meals(days=7)

    # Then
    # Should return empty list since no valid recipes were found
    assert meals == []


@pytest.mark.asyncio
async def test_generate_recipe_with_meal_context_disabled(
    mock_llm: MagicMock, mock_meal_repository: AsyncMock, mock_recipe_repository: AsyncMock
) -> None:
    """
    Given: Generator with repositories
    When: generate_recipe is called with include_meal_context=False
    Then: Meal context is NOT fetched or included
    """
    # Given
    mock_meal_repository.get_meals_for_date_range.return_value = []

    # Mock the workflow to return a proper recipe
    mock_workflow_result = {
        "instruction": "Create a new recipe",
        "recent_meals": [],
        "attempts": 1,
        "max_attempts": 3,
        "error": None,
        "recipe": {
            "title": "New Recipe",
            "summary": "A new recipe",
            "ingredients": ["ingredient1"],
            "instructions": ["step1"],
            "servings": 2,
            "prep_time": "5 min",
            "cook_time": "10 min",
            "difficulty": "easy",
        },
    }

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # Mock the workflow's ainvoke method
    mock_workflow = AsyncMock(return_value=mock_workflow_result)
    generator._workflow = MagicMock(ainvoke=mock_workflow)

    # When
    with patch.object(generator, "_get_recent_meals", new_callable=AsyncMock) as mock_get_meals:
        result = await generator.generate_recipe("Create a new recipe", include_meal_context=False)

    # Then
    assert result is not None
    assert result.title == "New Recipe"
    mock_get_meals.assert_not_called()


@pytest.mark.asyncio
async def test_generate_recipe_default_includes_context(
    mock_llm: MagicMock,
    mock_meal_repository: AsyncMock,
    mock_recipe_repository: AsyncMock,
    mock_recipe: Recipe,
) -> None:
    """
    Given: Generator with repositories and meals
    When: generate_recipe is called without include_meal_context parameter
    Then: Meal context is included by default
    """
    # Given
    meal = Meal(
        id=1,
        date=date(2026, 11, 20),
        moment=MealMoment.DINNER,
        recipe_id=1,
    )

    mock_meal_repository.get_meals_for_date_range.return_value = [meal]
    mock_recipe_repository.get_by_id = AsyncMock(return_value=mock_recipe)

    # Mock the workflow to return a proper recipe
    mock_workflow_result = {
        "instruction": "Create a new recipe",
        "recent_meals": [mock_recipe],
        "attempts": 1,
        "max_attempts": 3,
        "error": None,
        "recipe": {
            "title": "New Recipe",
            "summary": "A new recipe",
            "ingredients": ["ingredient1"],
            "instructions": ["step1"],
            "servings": 2,
            "prep_time": "5 min",
            "cook_time": "10 min",
            "difficulty": "easy",
        },
    }

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # Mock the workflow's ainvoke method
    mock_workflow = AsyncMock(return_value=mock_workflow_result)
    generator._workflow = MagicMock(ainvoke=mock_workflow)

    # When
    with patch.object(generator, "_get_recent_meals", new_callable=AsyncMock) as mock_get_meals:
        mock_get_meals.return_value = [mock_recipe]
        result = await generator.generate_recipe("Create a new recipe")

    # Then
    assert result is not None
    assert result.title == "New Recipe"
    mock_get_meals.assert_called_once_with(days=7)


# =============================================================================
# Test: Error Handling
# =============================================================================


@pytest.mark.asyncio
async def test_generate_recipe_meal_context_error(
    mock_llm: MagicMock, mock_meal_repository: AsyncMock, mock_recipe_repository: AsyncMock
) -> None:
    """
    Given: Meal repository raises an error
    When: generate_recipe is called with include_meal_context=True
    Then: Error is propagated to caller
    """
    # Given
    mock_meal_repository.get_meals_for_date_range.side_effect = Exception("Database error")

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # When/Then
    with pytest.raises(Exception, match="Database error"):
        await generator.generate_recipe("Create a new recipe", include_meal_context=True)


@pytest.mark.asyncio
async def test_generate_recipe_with_empty_meal_history_works(
    mock_llm: MagicMock, mock_meal_repository: AsyncMock, mock_recipe_repository: AsyncMock
) -> None:
    """
    Given: Generator whose repositories return no meals
    When: generate_recipe is called
    Then: Works and generates a recipe
    """
    # Given
    mock_meal_repository.get_meals_for_date_range.return_value = []

    # Mock the workflow to return a proper recipe
    mock_workflow_result = {
        "instruction": "Create a new recipe",
        "recent_meals": [],
        "attempts": 1,
        "max_attempts": 3,
        "error": None,
        "recipe": {
            "title": "New Recipe",
            "summary": "A new recipe",
            "ingredients": ["ingredient1"],
            "instructions": ["step1"],
            "servings": 2,
            "prep_time": "5 min",
            "cook_time": "10 min",
            "difficulty": "easy",
        },
    }

    generator = RecipeAIGenerator(
        llm=mock_llm,
        max_attempts=3,
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )

    # Mock the workflow's ainvoke method
    mock_workflow = AsyncMock(return_value=mock_workflow_result)
    generator._workflow = MagicMock(ainvoke=mock_workflow)

    # When
    result = await generator.generate_recipe("Create a new recipe", include_meal_context=True)

    # Then
    assert result is not None
    assert result.title == "New Recipe"
