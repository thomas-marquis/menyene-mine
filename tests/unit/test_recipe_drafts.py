"""Unit tests for Recipe Draft functionality."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.domain.entities.recipe_draft import RecipeDraft, RecipeDraftStatus
from src.domain.ports.ai_recipe_generator import AIRecipeGeneratorPort
from src.infra.repositories.recipe_draft_repository import RecipeDraftRepositoryImpl
from src.services.ai_recipe_generator import MockRecipeAIGenerator
from src.use_cases.recipe_draft_use_cases import RecipeDraftUseCases


def get_mock_ai_generator() -> AIRecipeGeneratorPort:
    """Helper to get a mock AI generator for tests."""
    return MockRecipeAIGenerator(max_recipes=10)


class TestRecipeDraftEntity:
    """Tests for RecipeDraft entity."""

    def test_should_create_draft_with_default_values(self) -> None:
        # Given/When
        draft = RecipeDraft()

        # Then
        assert draft.id is None
        assert draft.user_prompt is None
        assert draft.generated_content is None
        assert draft.status == RecipeDraftStatus.DRAFT
        assert draft.created_at is None
        assert draft.updated_at is None
        assert draft.recipe_id is None

    def test_should_create_draft_with_custom_values(self) -> None:
        # Given
        now = datetime.now()
        custom_content = {"title": "Test Recipe", "content": "Test content"}

        # When
        draft = RecipeDraft(
            id=1,
            user_prompt="Create a test recipe",
            generated_content=custom_content,
            status=RecipeDraftStatus.VALIDATED,
            created_at=now,
            updated_at=now,
            recipe_id=100,
        )

        # Then
        assert draft.id == 1
        assert draft.user_prompt == "Create a test recipe"
        assert draft.generated_content == custom_content
        assert draft.status == RecipeDraftStatus.VALIDATED
        assert draft.created_at == now
        assert draft.updated_at == now
        assert draft.recipe_id == 100


class TestRecipeDraftStatus:
    """Tests for RecipeDraftStatus enum."""

    def test_should_have_correct_status_values(self) -> None:
        # Then
        assert RecipeDraftStatus.DRAFT.value == "draft"
        assert RecipeDraftStatus.VALIDATED.value == "validated"
        assert RecipeDraftStatus.REJECTED.value == "rejected"


class TestRecipeAIGenerator:
    """Tests for AI Recipe Generator."""

    @pytest.mark.asyncio
    async def test_should_generate_mock_recipes_when_no_api_key(self) -> None:
        # Given
        generator: AIRecipeGeneratorPort = MockRecipeAIGenerator(max_recipes=10)

        # When
        recipes = await generator.generate_recipes("Create a pasta recipe", 3)

        # Then
        assert len(recipes) == 3
        assert all(isinstance(r, dict) for r in recipes)
        assert all("title" in r for r in recipes)
        assert all("content" in r for r in recipes)
        assert all("summary" in r for r in recipes)

    @pytest.mark.asyncio
    async def test_should_generate_correct_number_of_recipes(self) -> None:
        # Given
        generator: AIRecipeGeneratorPort = MockRecipeAIGenerator(max_recipes=10)

        # When
        recipes = await generator.generate_recipes("Create a recipe", 5)

        # Then
        assert len(recipes) == 5

    @pytest.mark.asyncio
    async def test_should_generate_recipes_with_required_fields(self) -> None:
        # Given
        generator: AIRecipeGeneratorPort = MockRecipeAIGenerator(max_recipes=10)

        # When
        recipes = await generator.generate_recipes("Create a cake recipe", 1)

        # Then
        assert len(recipes) == 1
        recipe = recipes[0]
        assert "title" in recipe
        assert "content" in recipe
        assert "summary" in recipe
        assert isinstance(recipe["title"], str)
        assert isinstance(recipe["content"], str)
        assert isinstance(recipe["summary"], str)

    @pytest.mark.asyncio
    async def test_should_generate_different_recipes_for_different_prompts(self) -> None:
        # Given
        generator: AIRecipeGeneratorPort = MockRecipeAIGenerator(max_recipes=10)

        # When
        pasta_recipes = await generator.generate_recipes("Create a pasta recipe", 1)
        salad_recipes = await generator.generate_recipes("Create a salad recipe", 1)

        # Then
        assert len(pasta_recipes) == 1
        assert len(salad_recipes) == 1
        # Titles should be different (with high probability)
        assert pasta_recipes[0]["title"] != salad_recipes[0]["title"]


class TestRecipeDraftUseCases:
    """Tests for Recipe Draft Use Cases."""

    @pytest.mark.asyncio
    async def test_should_generate_drafts_when_valid_prompt_provided(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        mock_generator = AsyncMock()
        
        mock_recipes = [
            {"title": "Recipe 1", "content": "Content 1", "summary": "Summary 1"},
            {"title": "Recipe 2", "content": "Content 2", "summary": "Summary 2"},
        ]
        mock_generator.generate_recipes.return_value = mock_recipes
        
        mock_draft = RecipeDraft(
            id=1,
            user_prompt="Test prompt",
            generated_content=mock_recipes[0],
            status=RecipeDraftStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_draft_repo.create.return_value = mock_draft
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=mock_generator,
        )

        # When
        result = await use_cases.generate_drafts("Test prompt", 2)

        # Then
        assert len(result) == 2
        mock_generator.generate_recipes.assert_called_once_with("Test prompt", 2)
        assert mock_draft_repo.create.call_count == 2

    @pytest.mark.asyncio
    async def test_should_get_draft_by_id(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_draft = RecipeDraft(
            id=1,
            user_prompt="Test prompt",
            generated_content={"title": "Test"},
            status=RecipeDraftStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_draft_repo.get_by_id.return_value = mock_draft
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        result = await use_cases.get_draft(1)

        # Then
        assert result is not None
        assert result.id == 1
        mock_draft_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_should_return_none_when_draft_not_found(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_draft_repo.get_by_id.return_value = None
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        result = await use_cases.get_draft(999)

        # Then
        assert result is None
        mock_draft_repo.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_should_list_all_drafts(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_drafts = [
            RecipeDraft(
                id=1,
                user_prompt="Prompt 1",
                generated_content={},
                status=RecipeDraftStatus.DRAFT,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            RecipeDraft(
                id=2,
                user_prompt="Prompt 2",
                generated_content={},
                status=RecipeDraftStatus.VALIDATED,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        mock_draft_repo.list_all.return_value = mock_drafts
        mock_draft_repo.count_by_status.return_value = 2
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        result = await use_cases.list_drafts()

        # Then
        assert len(result) == 2
        mock_draft_repo.list_all.assert_called_once_with(skip=0, limit=100, status=None)

    @pytest.mark.asyncio
    async def test_should_filter_drafts_by_status(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_draft = RecipeDraft(
            id=1,
            user_prompt="Test prompt",
            generated_content={},
            status=RecipeDraftStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_draft_repo.list_all.return_value = [mock_draft]
        mock_draft_repo.count_by_status.return_value = 1
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        result = await use_cases.list_drafts(status=RecipeDraftStatus.DRAFT)

        # Then
        assert len(result) == 1
        mock_draft_repo.list_all.assert_called_once_with(
            skip=0, limit=100, status=RecipeDraftStatus.DRAFT
        )

    @pytest.mark.asyncio
    async def test_should_validate_draft_and_create_recipe(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_draft = RecipeDraft(
            id=1,
            user_prompt="Test prompt",
            generated_content={
                "title": "Test Recipe",
                "content": "Test content",
                "summary": "Test summary",
            },
            status=RecipeDraftStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_draft_repo.get_by_id.return_value = mock_draft
        
        from src.domain.entities.recipe import Recipe
        mock_recipe = Recipe(
            id=100,
            title="Test Recipe",
            content="Test content",
            summary="Test summary",
        )
        mock_recipe_repo.create.return_value = mock_recipe
        
        mock_updated_draft = RecipeDraft(
            id=1,
            user_prompt="Test prompt",
            generated_content=mock_draft.generated_content,
            status=RecipeDraftStatus.VALIDATED,
            created_at=mock_draft.created_at,
            updated_at=datetime.now(),
            recipe_id=100,
        )
        mock_draft_repo.update.return_value = mock_updated_draft
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        result = await use_cases.validate_draft(1)

        # Then
        assert result is not None
        assert result.id == 100
        assert result.title == "Test Recipe"
        mock_draft_repo.get_by_id.assert_called_once_with(1)
        mock_recipe_repo.create.assert_called_once()
        mock_draft_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_none_when_validating_nonexistent_draft(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_draft_repo.get_by_id.return_value = None
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        result = await use_cases.validate_draft(999)

        # Then
        assert result is None
        mock_draft_repo.get_by_id.assert_called_once_with(999)
        mock_recipe_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_reject_draft(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_draft = RecipeDraft(
            id=1,
            user_prompt="Test prompt",
            generated_content={},
            status=RecipeDraftStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_draft_repo.get_by_id.return_value = mock_draft
        
        mock_updated_draft = RecipeDraft(
            id=1,
            user_prompt="Test prompt",
            generated_content={},
            status=RecipeDraftStatus.REJECTED,
            created_at=mock_draft.created_at,
            updated_at=datetime.now(),
        )
        mock_draft_repo.update.return_value = mock_updated_draft
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        result = await use_cases.reject_draft(1)

        # Then
        assert result is not None
        assert result.status == RecipeDraftStatus.REJECTED
        mock_draft_repo.get_by_id.assert_called_once_with(1)
        mock_draft_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_none_when_rejecting_nonexistent_draft(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_draft_repo.get_by_id.return_value = None
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        result = await use_cases.reject_draft(999)

        # Then
        assert result is None
        mock_draft_repo.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_should_delete_draft(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_draft_repo.delete.return_value = True
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        result = await use_cases.delete_draft(1)

        # Then
        assert result is True
        mock_draft_repo.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_should_return_false_when_deleting_nonexistent_draft(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_draft_repo.delete.return_value = False
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        result = await use_cases.delete_draft(999)

        # Then
        assert result is False
        mock_draft_repo.delete.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_should_get_draft_stats(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        
        mock_draft_repo.count_by_status.side_effect = [10, 5, 3, 2]
        
        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            ai_generator=get_mock_ai_generator(),
        )

        # When
        stats = await use_cases.get_draft_stats()

        # Then
        assert stats["total"] == 10
        assert stats["draft"] == 5
        assert stats["validated"] == 3
        assert stats["rejected"] == 2
