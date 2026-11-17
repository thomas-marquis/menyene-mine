from datetime import datetime

from src.domain.entities.recipe_draft import RecipeDraft, RecipeDraftContent, RecipeDraftStatus


class TestRecipeDraftEntity:
    """Tests for RecipeDraft entity."""

    def test_should_create_draft_with_default_values(self) -> None:
        # Given/When
        draft = RecipeDraft()

        # Then
        assert draft.id is None
        assert draft.user_instruction is None
        assert draft.generated_content is None
        assert draft.status == RecipeDraftStatus.DRAFT
        assert draft.created_at is None
        assert draft.updated_at is None
        assert draft.recipe_id is None

    def test_should_create_draft_with_custom_values(self) -> None:
        # Given
        now = datetime.now()
        custom_content: RecipeDraftContent = {"title": "Test Recipe", "summary": "Test content"}

        # When
        draft = RecipeDraft(
            id=1,
            user_instruction="Create a test recipe",
            generated_content=custom_content,
            status=RecipeDraftStatus.VALIDATED,
            created_at=now,
            updated_at=now,
            recipe_id=100,
        )

        # Then
        assert draft.id == 1
        assert draft.user_instruction == "Create a test recipe"
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
