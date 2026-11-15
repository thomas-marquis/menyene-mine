from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.domain.entities.recipe import Recipe
from src.domain.entities.recipe_draft import RecipeDraft, RecipeDraftStatus
from src.infra.repositories.recipe_draft_repository import RecipeDraftRepositoryImpl
from src.services.mock_recipe_generator import MockRecipeAIGenerator
from src.services.recipe_generator import RecipeGenerator
from src.use_cases.recipe_draft_use_cases import RecipeDraftUseCases


def get_mock_ai_generator() -> RecipeGenerator:
    """Helper to get a mock AI generator for tests."""
    return MockRecipeAIGenerator()


def get_mock_llm_judge() -> AsyncMock:
    """Helper to get a mock LLM judge for tests."""
    mock_judge = AsyncMock()
    mock_judge.validate_instruction.return_value = None
    mock_judge.validate_recipe.return_value = None
    return mock_judge


class TestRecipeDraftUseCases:
    """Tests for Recipe Draft Use Cases."""

    @pytest.mark.asyncio
    async def test_should_generate_drafts_when_valid_instruction_provided(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()
        mock_generator = AsyncMock()

        mock_recipe = Recipe(title="Recipe 1", content="Content 1", summary="Summary 1")
        mock_generator.generate_recipe.return_value = mock_recipe

        mock_draft = RecipeDraft(
            id=1,
            user_instruction="Test instruction",
            generated_content=mock_recipe,
            status=RecipeDraftStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_draft_repo.create.return_value = mock_draft

        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            recipe_generator=mock_generator,
            judge=get_mock_llm_judge(),
        )

        # When
        result = await use_cases.generate_drafts("Test instruction", 2)

        # Then
        assert len(result) == 1
        mock_generator.generate_recipe.assert_called_once_with("Test instruction")
        assert mock_draft_repo.create.call_count == 1

    @pytest.mark.asyncio
    async def test_should_get_draft_by_id(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()

        mock_draft = RecipeDraft(
            id=1,
            user_instruction="Test instruction",
            generated_content={"title": "Test"},
            status=RecipeDraftStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_draft_repo.get_by_id.return_value = mock_draft

        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
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
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
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
                user_instruction="Instruction 1",
                generated_content={},
                status=RecipeDraftStatus.DRAFT,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            RecipeDraft(
                id=2,
                user_instruction="Instruction 2",
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
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
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
            user_instruction="Test instruction",
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
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
        )

        # When
        result = await use_cases.list_drafts(status=RecipeDraftStatus.DRAFT)

        # Then
        assert len(result) == 1
        mock_draft_repo.list_all.assert_called_once_with(skip=0, limit=100, status=RecipeDraftStatus.DRAFT)

    @pytest.mark.asyncio
    async def test_should_validate_draft_and_create_recipe(self) -> None:
        # Given
        mock_draft_repo = AsyncMock(spec=RecipeDraftRepositoryImpl)
        mock_recipe_repo = AsyncMock()

        mock_draft = RecipeDraft(
            id=1,
            user_instruction="Test instruction",
            generated_content=Recipe(title="Test Recipe", content="Test content", summary="Test summary"),
            status=RecipeDraftStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_draft_repo.get_by_id.return_value = mock_draft

        mock_recipe = Recipe(
            id=100,
            title="Test Recipe",
            content="Test content",
            summary="Test summary",
        )
        mock_recipe_repo.create.return_value = mock_recipe

        mock_updated_draft = RecipeDraft(
            id=1,
            user_instruction="Test instruction",
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
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
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
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
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
            user_instruction="Test instruction",
            generated_content={},
            status=RecipeDraftStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        mock_draft_repo.get_by_id.return_value = mock_draft

        mock_updated_draft = RecipeDraft(
            id=1,
            user_instruction="Test instruction",
            generated_content={},
            status=RecipeDraftStatus.REJECTED,
            created_at=mock_draft.created_at,
            updated_at=datetime.now(),
        )
        mock_draft_repo.update.return_value = mock_updated_draft

        use_cases = RecipeDraftUseCases(
            draft_repository=mock_draft_repo,
            recipe_repository=mock_recipe_repo,
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
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
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
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
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
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
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
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
            recipe_generator=get_mock_ai_generator(),
            judge=get_mock_llm_judge(),
        )

        # When
        stats = await use_cases.get_draft_stats()

        # Then
        assert stats["total"] == 10
        assert stats["draft"] == 5
        assert stats["validated"] == 3
        assert stats["rejected"] == 2
