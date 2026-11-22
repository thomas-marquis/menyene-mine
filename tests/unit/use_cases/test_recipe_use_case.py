from unittest.mock import AsyncMock

import pytest

from src.domain.entities.recipe import Recipe
from src.domain.entities.search_result import SearchResult
from src.infra.repositories.recipe_repository import RecipeRepositoryImpl
from src.use_cases.recipe_use_cases import RecipeUseCases


class TestRecipeUseCases:
    @pytest.mark.asyncio
    async def test_should_create_recipe_when_valid_data_provided(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_recipe = Recipe(
            id=1,
            title="Test Recipe",
            summary="Test summary",
            ingredients=["ingredient 1", "ingredient 2"],
            instructions=["step 1", "step 2"],
            servings=4,
            prep_time="10 minutes",
            cook_time="20 minutes",
            difficulty="Easy",
            creation_date=None,
            last_updated=None,
        )
        mock_repo.create.return_value = mock_recipe
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.create_recipe(
            title="Test Recipe",
            summary="Test summary",
            ingredients=["ingredient 1", "ingredient 2"],
            instructions=["step 1", "step 2"],
            servings=4,
            prep_time="10 minutes",
            cook_time="20 minutes",
            difficulty="Easy",
        )

        # Then
        assert result.title == "Test Recipe"
        assert result.summary == "Test summary"
        assert result.ingredients == ["ingredient 1", "ingredient 2"]
        assert result.instructions == ["step 1", "step 2"]
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_recipe_when_get_by_id_called(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_recipe = Recipe(
            id=1,
            title="Test Recipe",
            summary="Test summary",
            ingredients=["ingredient 1"],
            instructions=["step 1"],
            servings=4,
            prep_time="10 minutes",
            cook_time="20 minutes",
            difficulty="Easy",
            creation_date=None,
            last_updated=None,
        )
        mock_repo.get_by_id.return_value = mock_recipe
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.get_recipe(1)

        # Then
        assert result is not None
        assert result.id == 1
        assert result.title == "Test Recipe"
        mock_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_should_return_none_when_recipe_not_found(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_repo.get_by_id.return_value = None
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.get_recipe(999)

        # Then
        assert result is None
        mock_repo.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_should_update_recipe_when_valid_data_provided(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        existing_recipe = Recipe(
            id=1,
            title="Old Recipe",
            summary="Old summary",
            ingredients=["old ingredient"],
            instructions=["old step"],
            servings=2,
            prep_time="5 minutes",
            cook_time="10 minutes",
            difficulty="Hard",
            creation_date=None,
            last_updated=None,
        )
        updated_recipe = Recipe(
            id=1,
            title="Updated Recipe",
            summary="Updated summary",
            ingredients=["new ingredient"],
            instructions=["new step"],
            servings=4,
            prep_time="10 minutes",
            cook_time="20 minutes",
            difficulty="Easy",
            creation_date=None,
            last_updated=None,
        )
        mock_repo.get_by_id.return_value = existing_recipe
        mock_repo.update.return_value = updated_recipe
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.update_recipe(
            recipe_id=1,
            title="Updated Recipe",
            summary="Updated summary",
            ingredients=["new ingredient"],
            instructions=["new step"],
            servings=4,
            prep_time="10 minutes",
            cook_time="20 minutes",
            difficulty="Easy",
        )

        # Then
        assert result is not None
        assert result.title == "Updated Recipe"
        assert result.ingredients == ["new ingredient"]
        mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_none_when_update_nonexistent_recipe(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_repo.get_by_id.return_value = None
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.update_recipe(
            recipe_id=999,
            title="Updated Recipe",
            summary="Updated summary",
            ingredients=["ingredient"],
            instructions=["step"],
        )

        # Then
        assert result is None
        mock_repo.get_by_id.assert_called_once_with(999)
        mock_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_delete_recipe_when_exists(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_repo.delete.return_value = True
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.delete_recipe(1)

        # Then
        assert result is True
        mock_repo.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_should_return_false_when_delete_nonexistent_recipe(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_repo.delete.return_value = False
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.delete_recipe(999)

        # Then
        assert result is False
        mock_repo.delete.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_no_recipes_exist(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_repo.list_all.return_value = SearchResult(recipes=[], total=0, skip=0, limit=100)
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.list_recipes()

        # Then
        assert result.recipes == []
        assert result.total == 0
        mock_repo.list_all.assert_called_once_with(skip=0, limit=100)

    @pytest.mark.asyncio
    async def test_should_return_recipes_when_list_called(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_recipes = [
            Recipe(
                id=1,
                title="Recipe 1",
                summary="Summary 1",
                ingredients=["ingredient 1"],
                instructions=["step 1"],
                servings=4,
                prep_time="10 minutes",
                cook_time="20 minutes",
                difficulty="Easy",
                creation_date=None,
                last_updated=None,
            ),
            Recipe(
                id=2,
                title="Recipe 2",
                summary="Summary 2",
                ingredients=["ingredient 2"],
                instructions=["step 2"],
                servings=4,
                prep_time="10 minutes",
                cook_time="20 minutes",
                difficulty="Easy",
                creation_date=None,
                last_updated=None,
            ),
        ]
        mock_repo.list_all.return_value = SearchResult(recipes=mock_recipes, total=2, skip=0, limit=10)
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.list_recipes(skip=0, limit=10)

        # Then
        assert len(result.recipes) == 2
        assert result.recipes[0].title == "Recipe 1"
        assert result.recipes[1].title == "Recipe 2"
        mock_repo.list_all.assert_called_once_with(skip=0, limit=10)

    @pytest.mark.asyncio
    async def test_should_return_recipes_when_search_called(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_recipes = [
            Recipe(
                id=1,
                title="Pasta Recipe",
                summary="Pasta summary",
                ingredients=["pasta", "tomato"],
                instructions=["cook pasta"],
                servings=4,
                prep_time="10 minutes",
                cook_time="20 minutes",
                difficulty="Easy",
                creation_date=None,
                last_updated=None,
            ),
        ]
        mock_repo.search.return_value = SearchResult(recipes=mock_recipes, total=1, query="pasta", skip=0, limit=100)
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.search_recipes(keyword="pasta")

        # Then
        assert len(result.recipes) == 1
        assert result.recipes[0].title == "Pasta Recipe"
        mock_repo.search.assert_called_once_with(keyword="pasta", skip=0, limit=100)

    @pytest.mark.asyncio
    async def test_should_reorder_instructions_when_valid_data_provided(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        existing_recipe = Recipe(
            id=1,
            title="Test Recipe",
            summary="Test summary",
            ingredients=["ingredient 1", "ingredient 2"],
            instructions=["step 1", "step 2", "step 3"],
            servings=4,
            prep_time="10 minutes",
            cook_time="20 minutes",
            difficulty="Easy",
            creation_date=None,
            last_updated=None,
        )
        updated_recipe = Recipe(
            id=1,
            title="Test Recipe",
            summary="Test summary",
            ingredients=["ingredient 1", "ingredient 2"],
            instructions=["step 2", "step 1", "step 3"],  # Reordered
            servings=4,
            prep_time="10 minutes",
            cook_time="20 minutes",
            difficulty="Easy",
            creation_date=None,
            last_updated=None,
        )
        mock_repo.get_by_id.return_value = existing_recipe
        mock_repo.update.return_value = updated_recipe
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.reorder_instructions(
            recipe_id=1,
            instructions=["step 2", "step 1", "step 3"],
        )

        # Then
        assert result is not None
        assert result.instructions == ["step 2", "step 1", "step 3"]
        assert result.title == "Test Recipe"  # Other fields should remain unchanged
        assert result.ingredients == ["ingredient 1", "ingredient 2"]
        mock_repo.get_by_id.assert_called_once_with(1)
        mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_none_when_reorder_instructions_nonexistent_recipe(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=RecipeRepositoryImpl)
        mock_repo.get_by_id.return_value = None
        use_cases = RecipeUseCases(mock_repo)

        # When
        result = await use_cases.reorder_instructions(
            recipe_id=999,
            instructions=["step 2", "step 1"],
        )

        # Then
        assert result is None
        mock_repo.get_by_id.assert_called_once_with(999)
        mock_repo.update.assert_not_called()
