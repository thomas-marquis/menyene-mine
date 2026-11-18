from unittest.mock import AsyncMock

import pytest

from src.domain.entities.stats import AppStats, DraftStats, GroceryStats, RecipeStats
from src.infra.repositories.grocery_repository import GroceryRepositoryImpl
from src.infra.repositories.recipe_draft_repository import RecipeDraftRepositoryImpl
from src.infra.repositories.recipe_repository import RecipeRepositoryImpl
from src.use_cases.stats_use_cases import StatsUseCases


class TestStatsUseCases:
    @pytest.mark.asyncio
    async def test_should_return_stats_with_zero_counts_when_no_resources_exist(self) -> None:
        # Given
        mock_recipe_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_grocery_repo = AsyncMock(spec=GroceryRepositoryImpl)

        mock_recipe_repo.count_all.return_value = 0
        mock_draft_repo.get_status_counts.return_value = DraftStats(
            total_count=0,
            draft_count=0,
            validated_count=0,
            rejected_count=0,
        )
        mock_grocery_repo.count_all.return_value = 0
        mock_grocery_repo.count_by_completed.return_value = 0

        use_cases = StatsUseCases(
            recipe_repository=mock_recipe_repo,
            draft_repository=mock_draft_repo,
            grocery_repository=mock_grocery_repo,
        )

        # When
        result = await use_cases.get_all_stats()

        # Then
        assert isinstance(result, AppStats)
        assert result.recipes.total_count == 0
        assert result.drafts.total_count == 0
        assert result.drafts.draft_count == 0
        assert result.drafts.validated_count == 0
        assert result.drafts.rejected_count == 0
        assert result.groceries.total_count == 0
        assert result.groceries.active_count == 0
        assert result.groceries.completed_count == 0

    @pytest.mark.asyncio
    async def test_should_return_correct_stats_when_resources_exist(self) -> None:
        # Given
        mock_recipe_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_grocery_repo = AsyncMock(spec=GroceryRepositoryImpl)

        mock_recipe_repo.count_all.return_value = 10
        mock_draft_repo.get_status_counts.return_value = DraftStats(
            total_count=15,
            draft_count=8,
            validated_count=5,
            rejected_count=2,
        )
        mock_grocery_repo.count_all.return_value = 20
        mock_grocery_repo.count_by_completed.return_value = 7

        use_cases = StatsUseCases(
            recipe_repository=mock_recipe_repo,
            draft_repository=mock_draft_repo,
            grocery_repository=mock_grocery_repo,
        )

        # When
        result = await use_cases.get_all_stats()

        # Then
        assert isinstance(result, AppStats)
        assert isinstance(result.recipes, RecipeStats)
        assert isinstance(result.drafts, DraftStats)
        assert isinstance(result.groceries, GroceryStats)

        assert result.recipes.total_count == 10
        assert result.drafts.total_count == 15
        assert result.drafts.draft_count == 8
        assert result.drafts.validated_count == 5
        assert result.drafts.rejected_count == 2
        assert result.groceries.total_count == 20
        assert result.groceries.completed_count == 7
        assert result.groceries.active_count == 13  # 20 total - 7 completed

    @pytest.mark.asyncio
    async def test_should_calculate_active_groceries_correctly(self) -> None:
        # Given
        mock_recipe_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_grocery_repo = AsyncMock(spec=GroceryRepositoryImpl)

        mock_recipe_repo.count_all.return_value = 5
        mock_draft_repo.get_status_counts.return_value = DraftStats(
            total_count=3,
            draft_count=2,
            validated_count=1,
            rejected_count=0,
        )
        mock_grocery_repo.count_all.return_value = 10
        mock_grocery_repo.count_by_completed.return_value = 3

        use_cases = StatsUseCases(
            recipe_repository=mock_recipe_repo,
            draft_repository=mock_draft_repo,
            grocery_repository=mock_grocery_repo,
        )

        # When
        result = await use_cases.get_all_stats()

        # Then
        assert result.groceries.total_count == 10
        assert result.groceries.completed_count == 3
        assert result.groceries.active_count == 7  # 10 - 3 = 7

    @pytest.mark.asyncio
    async def test_should_call_all_repository_methods(self) -> None:
        # Given
        mock_recipe_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_grocery_repo = AsyncMock(spec=GroceryRepositoryImpl)

        mock_recipe_repo.count_all.return_value = 0
        mock_draft_repo.get_status_counts.return_value = DraftStats(
            total_count=0,
            draft_count=0,
            validated_count=0,
            rejected_count=0,
        )
        mock_grocery_repo.count_all.return_value = 0
        mock_grocery_repo.count_by_completed.return_value = 0

        use_cases = StatsUseCases(
            recipe_repository=mock_recipe_repo,
            draft_repository=mock_draft_repo,
            grocery_repository=mock_grocery_repo,
        )

        # When
        await use_cases.get_all_stats()

        # Then
        mock_recipe_repo.count_all.assert_called_once()
        mock_draft_repo.get_status_counts.assert_called_once()
        mock_grocery_repo.count_all.assert_called_once()
        mock_grocery_repo.count_by_completed.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_should_return_stats_with_large_numbers(self) -> None:
        # Given
        mock_recipe_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_grocery_repo = AsyncMock(spec=GroceryRepositoryImpl)

        mock_recipe_repo.count_all.return_value = 150
        mock_draft_repo.get_status_counts.return_value = DraftStats(
            total_count=200,
            draft_count=100,
            validated_count=75,
            rejected_count=25,
        )
        mock_grocery_repo.count_all.return_value = 300
        mock_grocery_repo.count_by_completed.return_value = 50

        use_cases = StatsUseCases(
            recipe_repository=mock_recipe_repo,
            draft_repository=mock_draft_repo,
            grocery_repository=mock_grocery_repo,
        )

        # When
        result = await use_cases.get_all_stats()

        # Then
        assert result.recipes.total_count == 150
        assert result.drafts.total_count == 200
        assert result.drafts.draft_count == 100
        assert result.groceries.total_count == 300
        assert result.groceries.active_count == 250
        assert result.groceries.completed_count == 50

    @pytest.mark.asyncio
    async def test_should_handle_all_drafts_completed(self) -> None:
        # Given
        mock_recipe_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_grocery_repo = AsyncMock(spec=GroceryRepositoryImpl)

        mock_recipe_repo.count_all.return_value = 0
        mock_draft_repo.get_status_counts.return_value = DraftStats(
            total_count=10,
            draft_count=0,
            validated_count=8,
            rejected_count=2,
        )
        mock_grocery_repo.count_all.return_value = 0
        mock_grocery_repo.count_by_completed.return_value = 0

        use_cases = StatsUseCases(
            recipe_repository=mock_recipe_repo,
            draft_repository=mock_draft_repo,
            grocery_repository=mock_grocery_repo,
        )

        # When
        result = await use_cases.get_all_stats()

        # Then
        assert result.drafts.total_count == 10
        assert result.drafts.draft_count == 0
        assert result.drafts.validated_count == 8
        assert result.drafts.rejected_count == 2

    @pytest.mark.asyncio
    async def test_should_handle_all_groceries_completed(self) -> None:
        # Given
        mock_recipe_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_grocery_repo = AsyncMock(spec=GroceryRepositoryImpl)

        mock_recipe_repo.count_all.return_value = 0
        mock_draft_repo.get_status_counts.return_value = DraftStats(
            total_count=0,
            draft_count=0,
            validated_count=0,
            rejected_count=0,
        )
        mock_grocery_repo.count_all.return_value = 10
        mock_grocery_repo.count_by_completed.return_value = 10

        use_cases = StatsUseCases(
            recipe_repository=mock_recipe_repo,
            draft_repository=mock_draft_repo,
            grocery_repository=mock_grocery_repo,
        )

        # When
        result = await use_cases.get_all_stats()

        # Then
        assert result.groceries.total_count == 10
        assert result.groceries.completed_count == 10
        assert result.groceries.active_count == 0  # All completed
