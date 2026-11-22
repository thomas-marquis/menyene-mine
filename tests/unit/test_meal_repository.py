from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.entities.meal import Meal, MealMoment
from src.infra.repositories.meal_repository import MealRepositoryImpl


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock AsyncSession for testing."""
    mock_session = AsyncMock()
    return mock_session


@pytest.fixture
def meal_repository(mock_session: AsyncMock) -> MealRepositoryImpl:
    """Create a MealRepositoryImpl instance with mock session."""
    return MealRepositoryImpl(mock_session)


class TestCreate:
    @pytest.mark.asyncio
    async def test_should_create_meal(self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock) -> None:
        # Given
        meal = Meal(
            date=date(2026, 11, 18),
            moment=MealMoment.LUNCH,
            recipe_id=1,
        )

        mock_meal_model = MagicMock()
        mock_meal_model.id = 1
        mock_meal_model.date = date(2026, 11, 18)
        mock_meal_model.moment = "lunch"
        mock_meal_model.recipe_id = 1
        mock_meal_model.created_at = datetime(2026, 11, 18, 10, 0)
        mock_meal_model.updated_at = datetime(2026, 11, 18, 10, 0)

        # Mock the session operations
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Mock the MealModel constructor to return our mock
        with patch(
            "src.infra.repositories.meal_repository.MealModel",
            return_value=mock_meal_model,
        ):
            # When
            result = await meal_repository.create(meal)

            # Then
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()
            assert result.id == 1
            assert result.date == date(2026, 11, 18)
            assert result.moment == MealMoment.LUNCH
            assert result.recipe_id == 1


class TestGetById:
    @pytest.mark.asyncio
    async def test_should_return_meal_when_exists(
        self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock
    ) -> None:
        # Given
        test_meal_id = 1
        mock_meal_model = MagicMock()
        mock_meal_model.id = test_meal_id
        mock_meal_model.date = date(2026, 11, 18)
        mock_meal_model.moment = "lunch"
        mock_meal_model.recipe_id = 1
        mock_meal_model.created_at = datetime(2026, 11, 18, 10, 0)
        mock_meal_model.updated_at = datetime(2026, 11, 18, 10, 0)

        # Mock the select and scalar_one_or_none
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_meal_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.get_by_id(test_meal_id)

        # Then
        mock_session.execute.assert_called_once()
        assert result is not None
        assert result.id == test_meal_id
        assert result.date == date(2026, 11, 18)
        assert result.moment == MealMoment.LUNCH

    @pytest.mark.asyncio
    async def test_should_return_none_when_not_exists(
        self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock
    ) -> None:
        # Given
        test_meal_id = 999

        # Mock the select and scalar_one_or_none
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.get_by_id(test_meal_id)

        # Then
        assert result is None


class TestGetByDateAndMoment:
    @pytest.mark.asyncio
    async def test_should_return_meal_when_exists(
        self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock
    ) -> None:
        # Given
        test_date = date(2026, 11, 18)
        test_moment = MealMoment.LUNCH
        mock_meal_model = MagicMock()
        mock_meal_model.id = 1
        mock_meal_model.date = test_date
        mock_meal_model.moment = "lunch"
        mock_meal_model.recipe_id = 1
        mock_meal_model.created_at = datetime(2026, 11, 18, 10, 0)
        mock_meal_model.updated_at = datetime(2026, 11, 18, 10, 0)

        # Mock the select and scalar_one_or_none
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_meal_model
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.get_by_date_and_moment(test_date, test_moment)

        # Then
        mock_session.execute.assert_called_once()
        assert result is not None
        assert result.id == 1
        assert result.date == test_date
        assert result.moment == test_moment

    @pytest.mark.asyncio
    async def test_should_return_none_when_not_exists(
        self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock
    ) -> None:
        # Given
        test_date = date(2026, 11, 18)
        test_moment = MealMoment.LUNCH

        # Mock the select and scalar_one_or_none
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.get_by_date_and_moment(test_date, test_moment)

        # Then
        assert result is None


class TestGetMealsForMonth:
    @pytest.mark.asyncio
    async def test_should_return_meals_for_month(
        self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock
    ) -> None:
        # Given
        test_year = 2026
        test_month = 11
        mock_meal_models = [
            MagicMock(
                id=1,
                date=date(2026, 11, 18),
                moment="lunch",
                recipe_id=1,
                created_at=datetime(2026, 11, 18, 10, 0),
                updated_at=datetime(2026, 11, 18, 10, 0),
            ),
            MagicMock(
                id=2,
                date=date(2026, 11, 19),
                moment="dinner",
                recipe_id=2,
                created_at=datetime(2026, 11, 19, 10, 0),
                updated_at=datetime(2026, 11, 19, 10, 0),
            ),
        ]

        # Mock the select and scalars
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_meal_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.get_meals_for_month(test_year, test_month)

        # Then
        mock_session.execute.assert_called_once()
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_no_meals(
        self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock
    ) -> None:
        # Given
        test_year = 2026
        test_month = 11

        # Mock the select and scalars
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.get_meals_for_month(test_year, test_month)

        # Then
        assert result == []


class TestUpdate:
    @pytest.mark.asyncio
    async def test_should_update_meal(self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock) -> None:
        # Given
        meal = Meal(
            id=1,
            date=date(2026, 11, 18),
            moment=MealMoment.LUNCH,
            recipe_id=2,  # New recipe_id
        )
        mock_meal_model = MagicMock()
        mock_meal_model.id = 1
        mock_meal_model.date = date(2026, 11, 18)
        mock_meal_model.moment = "lunch"
        mock_meal_model.recipe_id = 1  # Old recipe_id
        mock_meal_model.created_at = datetime(2026, 11, 18, 10, 0)
        mock_meal_model.updated_at = datetime(2026, 11, 18, 10, 0)

        # Mock the select and scalar_one_or_none
        mock_select_result = MagicMock()
        mock_select_result.scalar_one_or_none.return_value = mock_meal_model
        mock_session.execute = AsyncMock(return_value=mock_select_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # When
        result = await meal_repository.update(meal)

        # Then
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert result is not None
        assert result.recipe_id == 2

    @pytest.mark.asyncio
    async def test_should_return_none_when_not_exists(
        self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock
    ) -> None:
        # Given
        meal = Meal(
            id=999,
            date=date(2026, 11, 18),
            moment=MealMoment.LUNCH,
            recipe_id=2,
        )

        # Mock the select and scalar_one_or_none
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.update(meal)

        # Then
        assert result is None


class TestDelete:
    @pytest.mark.asyncio
    async def test_should_delete_meal(self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock) -> None:
        # Given
        test_meal_id = 1

        # Mock the delete and rowcount
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.delete(test_meal_id)

        # Then
        mock_session.execute.assert_called_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_should_return_false_when_not_exists(
        self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock
    ) -> None:
        # Given
        test_meal_id = 999

        # Mock the delete and rowcount
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.delete(test_meal_id)

        # Then
        assert result is False


class TestGetMealsByRecipeId:
    @pytest.mark.asyncio
    async def test_should_return_meals_for_recipe(
        self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock
    ) -> None:
        # Given
        test_recipe_id = 1
        mock_meal_models = [
            MagicMock(
                id=1,
                date=date(2026, 11, 18),
                moment="lunch",
                recipe_id=test_recipe_id,
                created_at=datetime(2026, 11, 18, 10, 0),
                updated_at=datetime(2026, 11, 18, 10, 0),
            ),
            MagicMock(
                id=2,
                date=date(2026, 11, 19),
                moment="dinner",
                recipe_id=test_recipe_id,
                created_at=datetime(2026, 11, 19, 10, 0),
                updated_at=datetime(2026, 11, 19, 10, 0),
            ),
        ]

        # Mock the select and scalars
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_meal_models
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.get_meals_by_recipe_id(test_recipe_id)

        # Then
        mock_session.execute.assert_called_once()
        assert len(result) == 2
        assert result[0].recipe_id == test_recipe_id
        assert result[1].recipe_id == test_recipe_id

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_no_meals(
        self, meal_repository: MealRepositoryImpl, mock_session: AsyncMock
    ) -> None:
        # Given
        test_recipe_id = 999

        # Mock the select and scalars
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await meal_repository.get_meals_by_recipe_id(test_recipe_id)

        # Then
        assert result == []
