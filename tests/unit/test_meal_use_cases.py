from datetime import date, datetime
from unittest.mock import AsyncMock

import pytest

from src.domain.entities.meal import Meal, MealMoment
from src.domain.entities.recipe import Recipe
from src.use_cases.meal_use_cases import MealUseCases


@pytest.fixture
def mock_meal_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_recipe_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def meal_use_cases(mock_meal_repository: AsyncMock, mock_recipe_repository: AsyncMock) -> MealUseCases:
    return MealUseCases(
        meal_repository=mock_meal_repository,
        recipe_repository=mock_recipe_repository,
    )


class TestCreateMeal:
    @pytest.mark.asyncio
    async def test_should_create_meal_when_recipe_exists(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
        mock_recipe_repository: AsyncMock,
    ) -> None:
        # Given
        test_date = date(2026, 11, 18)
        test_moment = MealMoment.LUNCH
        test_recipe_id = 1

        mock_recipe_repository.get_by_id.return_value = Recipe(id=test_recipe_id, title="Test Recipe")
        mock_meal_repository.get_by_date_and_moment.return_value = None
        mock_meal_repository.create.return_value = Meal(
            id=1,
            date=test_date,
            moment=test_moment,
            recipe_id=test_recipe_id,
            created_at=datetime(2026, 11, 18, 10, 0),
            updated_at=datetime(2026, 11, 18, 10, 0),
        )

        # When
        result = await meal_use_cases.create_meal(test_date, test_moment, test_recipe_id)

        # Then
        mock_recipe_repository.get_by_id.assert_called_once_with(test_recipe_id)
        mock_meal_repository.get_by_date_and_moment.assert_called_once_with(test_date, test_moment)
        mock_meal_repository.create.assert_called_once()
        assert result.recipe_id == test_recipe_id
        assert result.date == test_date
        assert result.moment == test_moment

    @pytest.mark.asyncio
    async def test_should_raise_error_when_recipe_does_not_exist(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
        mock_recipe_repository: AsyncMock,
    ) -> None:
        # Given
        test_date = date(2026, 11, 18)
        test_moment = MealMoment.LUNCH
        test_recipe_id = 999

        mock_recipe_repository.get_by_id.return_value = None

        # When / Then
        with pytest.raises(ValueError, match="Recipe with id 999 does not exist"):
            await meal_use_cases.create_meal(test_date, test_moment, test_recipe_id)

    @pytest.mark.asyncio
    async def test_should_raise_error_when_meal_already_exists(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
        mock_recipe_repository: AsyncMock,
    ) -> None:
        # Given
        test_date = date(2026, 11, 18)
        test_moment = MealMoment.LUNCH
        test_recipe_id = 1

        mock_recipe_repository.get_by_id.return_value = Recipe(id=test_recipe_id, title="Test Recipe")
        mock_meal_repository.get_by_date_and_moment.return_value = Meal(
            id=1,
            date=test_date,
            moment=test_moment,
            recipe_id=2,
        )

        # When / Then
        with pytest.raises(ValueError, match="A meal already exists"):
            await meal_use_cases.create_meal(test_date, test_moment, test_recipe_id)


class TestGetMeal:
    @pytest.mark.asyncio
    async def test_should_return_meal_when_exists(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
    ) -> None:
        # Given
        test_date = date(2026, 11, 18)
        test_moment = MealMoment.LUNCH
        expected_meal = Meal(
            id=1,
            date=test_date,
            moment=test_moment,
            recipe_id=1,
        )

        mock_meal_repository.get_by_date_and_moment.return_value = expected_meal

        # When
        result = await meal_use_cases.get_meal(test_date, test_moment)

        # Then
        mock_meal_repository.get_by_date_and_moment.assert_called_once_with(test_date, test_moment)
        assert result == expected_meal

    @pytest.mark.asyncio
    async def test_should_return_none_when_not_exists(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
    ) -> None:
        # Given
        test_date = date(2026, 11, 18)
        test_moment = MealMoment.LUNCH

        mock_meal_repository.get_by_date_and_moment.return_value = None

        # When
        result = await meal_use_cases.get_meal(test_date, test_moment)

        # Then
        assert result is None


class TestGetMealById:
    @pytest.mark.asyncio
    async def test_should_return_meal_when_exists(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
    ) -> None:
        # Given
        test_meal_id = 1
        expected_meal = Meal(
            id=test_meal_id,
            date=date(2026, 11, 18),
            moment=MealMoment.LUNCH,
            recipe_id=1,
        )

        mock_meal_repository.get_by_id.return_value = expected_meal

        # When
        result = await meal_use_cases.get_meal_by_id(test_meal_id)

        # Then
        mock_meal_repository.get_by_id.assert_called_once_with(test_meal_id)
        assert result == expected_meal

    @pytest.mark.asyncio
    async def test_should_return_none_when_not_exists(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
    ) -> None:
        # Given
        test_meal_id = 999

        mock_meal_repository.get_by_id.return_value = None

        # When
        result = await meal_use_cases.get_meal_by_id(test_meal_id)

        # Then
        assert result is None


class TestGetMealsForMonth:
    @pytest.mark.asyncio
    async def test_should_return_meals_for_month(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
    ) -> None:
        # Given
        test_year = 2026
        test_month = 11
        expected_meals = [
            Meal(
                id=1,
                date=date(2026, 11, 18),
                moment=MealMoment.LUNCH,
                recipe_id=1,
            ),
            Meal(
                id=2,
                date=date(2026, 11, 19),
                moment=MealMoment.DINNER,
                recipe_id=2,
            ),
        ]

        mock_meal_repository.get_meals_for_month.return_value = expected_meals

        # When
        result = await meal_use_cases.get_meals_for_month(test_year, test_month)

        # Then
        mock_meal_repository.get_meals_for_month.assert_called_once_with(test_year, test_month)
        assert result == expected_meals


class TestUpdateMeal:
    @pytest.mark.asyncio
    async def test_should_update_meal_when_recipe_exists(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
        mock_recipe_repository: AsyncMock,
    ) -> None:
        # Given
        test_meal_id = 1
        test_recipe_id = 2
        existing_meal = Meal(
            id=test_meal_id,
            date=date(2026, 11, 18),
            moment=MealMoment.LUNCH,
            recipe_id=1,
        )
        updated_meal = Meal(
            id=test_meal_id,
            date=date(2026, 11, 18),
            moment=MealMoment.LUNCH,
            recipe_id=test_recipe_id,
        )

        mock_recipe_repository.get_by_id.return_value = Recipe(id=test_recipe_id, title="New Recipe")
        mock_meal_repository.get_by_id.return_value = existing_meal
        mock_meal_repository.update.return_value = updated_meal

        # When
        result = await meal_use_cases.update_meal(test_meal_id, test_recipe_id)

        # Then
        mock_recipe_repository.get_by_id.assert_called_once_with(test_recipe_id)
        mock_meal_repository.get_by_id.assert_called_once_with(test_meal_id)
        mock_meal_repository.update.assert_called_once()
        assert result is not None
        assert result.recipe_id == test_recipe_id

    @pytest.mark.asyncio
    async def test_should_raise_error_when_recipe_does_not_exist(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
        mock_recipe_repository: AsyncMock,
    ) -> None:
        # Given
        test_meal_id = 1
        test_recipe_id = 999

        mock_recipe_repository.get_by_id.return_value = None

        # When / Then
        with pytest.raises(ValueError, match="Recipe with id 999 does not exist"):
            await meal_use_cases.update_meal(test_meal_id, test_recipe_id)

    @pytest.mark.asyncio
    async def test_should_return_none_when_meal_not_exists(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
        mock_recipe_repository: AsyncMock,
    ) -> None:
        # Given
        test_meal_id = 999
        test_recipe_id = 1

        mock_recipe_repository.get_by_id.return_value = Recipe(id=test_recipe_id, title="Test Recipe")
        mock_meal_repository.get_by_id.return_value = None

        # When
        result = await meal_use_cases.update_meal(test_meal_id, test_recipe_id)

        # Then
        assert result is None


class TestDeleteMeal:
    @pytest.mark.asyncio
    async def test_should_delete_meal_when_exists(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
    ) -> None:
        # Given
        test_meal_id = 1

        mock_meal_repository.delete.return_value = True

        # When
        result = await meal_use_cases.delete_meal(test_meal_id)

        # Then
        mock_meal_repository.delete.assert_called_once_with(test_meal_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_should_return_false_when_not_exists(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
    ) -> None:
        # Given
        test_meal_id = 999

        mock_meal_repository.delete.return_value = False

        # When
        result = await meal_use_cases.delete_meal(test_meal_id)

        # Then
        assert result is False


class TestGetMealsByRecipeId:
    @pytest.mark.asyncio
    async def test_should_return_meals_for_recipe(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
    ) -> None:
        # Given
        test_recipe_id = 1
        expected_meals = [
            Meal(
                id=1,
                date=date(2026, 11, 18),
                moment=MealMoment.LUNCH,
                recipe_id=test_recipe_id,
            ),
            Meal(
                id=2,
                date=date(2026, 11, 19),
                moment=MealMoment.DINNER,
                recipe_id=test_recipe_id,
            ),
        ]

        mock_meal_repository.get_meals_by_recipe_id.return_value = expected_meals

        # When
        result = await meal_use_cases.get_meals_by_recipe_id(test_recipe_id)

        # Then
        mock_meal_repository.get_meals_by_recipe_id.assert_called_once_with(test_recipe_id)
        assert result == expected_meals


class TestCheckRecipeHasMeals:
    @pytest.mark.asyncio
    async def test_should_return_true_when_recipe_has_meals(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
    ) -> None:
        # Given
        test_recipe_id = 1

        mock_meal_repository.get_meals_by_recipe_id.return_value = [
            Meal(
                id=1,
                date=date(2026, 11, 18),
                moment=MealMoment.LUNCH,
                recipe_id=test_recipe_id,
            ),
        ]

        # When
        result = await meal_use_cases.check_recipe_has_meals(test_recipe_id)

        # Then
        assert result is True

    @pytest.mark.asyncio
    async def test_should_return_false_when_recipe_has_no_meals(
        self,
        meal_use_cases: MealUseCases,
        mock_meal_repository: AsyncMock,
    ) -> None:
        # Given
        test_recipe_id = 1

        mock_meal_repository.get_meals_by_recipe_id.return_value = []

        # When
        result = await meal_use_cases.check_recipe_has_meals(test_recipe_id)

        # Then
        assert result is False
