"""
Use cases for Recipe Draft operations.
"""

from datetime import datetime
from typing import Any

from ..domain.entities.recipe import Recipe
from ..domain.entities.recipe_draft import RecipeDraft, RecipeDraftStatus
from ..domain.ports.ai_recipe_generator import AIRecipeGeneratorPort
from ..domain.ports.recipe_draft_repository import RecipeDraftRepositoryPort
from ..domain.ports.recipe_repository import RecipeRepositoryPort


class RecipeDraftUseCases:
    """Use cases for RecipeDraft operations."""

    def __init__(
        self,
        draft_repository: RecipeDraftRepositoryPort,
        recipe_repository: RecipeRepositoryPort,
        ai_generator: AIRecipeGeneratorPort,
    ) -> None:
        self.draft_repository = draft_repository
        self.recipe_repository = recipe_repository
        self.ai_generator = ai_generator

    async def generate_drafts(self, user_prompt: str, max_drafts: int = 10) -> list[RecipeDraft]:
        """
        Generate recipe drafts from a user prompt using AI.

        Args:
            user_prompt: The user's instruction for recipe generation
            max_drafts: Maximum number of drafts to generate (configurable)

        Returns:
            List of created RecipeDraft entities
        """
        # Generate recipes using AI
        recipes = await self.ai_generator.generate_recipes(user_prompt, max_drafts)

        # Create draft entities for each generated recipe
        drafts = []
        for recipe_data in recipes:
            draft = RecipeDraft(
                user_prompt=user_prompt,
                generated_content=recipe_data,
                status=RecipeDraftStatus.DRAFT,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            created_draft = await self.draft_repository.create(draft)
            drafts.append(created_draft)

        return drafts

    async def get_draft(self, draft_id: int) -> RecipeDraft | None:
        """Get a specific recipe draft by ID."""
        return await self.draft_repository.get_by_id(draft_id)

    async def list_drafts(
        self, skip: int = 0, limit: int = 100, status: RecipeDraftStatus | None = None
    ) -> list[RecipeDraft]:
        """List all recipe drafts with optional filtering."""
        return await self.draft_repository.list_all(skip=skip, limit=limit, status=status)

    async def count_drafts(self, status: RecipeDraftStatus | None = None) -> int:
        """Count recipe drafts by status."""
        return await self.draft_repository.count_by_status(status)

    async def validate_draft(self, draft_id: int) -> Recipe | None:
        """
        Validate a draft and create an actual recipe from it.

        Args:
            draft_id: The ID of the draft to validate

        Returns:
            The created Recipe entity, or None if draft not found
        """
        # Get the draft
        draft = await self.draft_repository.get_by_id(draft_id)
        if draft is None:
            return None

        # Extract recipe data from generated content
        content = draft.generated_content or {}
        title = content.get("title", "Untitled Recipe")
        recipe_content = content.get("content", "")
        summary = content.get("summary", "")

        # Create the actual recipe
        recipe = Recipe(
            title=title,
            content=recipe_content,
            summary=summary,
        )
        created_recipe = await self.recipe_repository.create(recipe)

        # Update the draft to mark it as validated and link to the recipe
        draft.status = RecipeDraftStatus.VALIDATED
        draft.recipe_id = created_recipe.id
        draft.updated_at = datetime.now()
        await self.draft_repository.update(draft)

        return created_recipe

    async def reject_draft(self, draft_id: int) -> RecipeDraft | None:
        """
        Reject a draft.

        Args:
            draft_id: The ID of the draft to reject

        Returns:
            The updated RecipeDraft entity, or None if not found
        """
        draft = await self.draft_repository.get_by_id(draft_id)
        if draft is None:
            return None

        draft.status = RecipeDraftStatus.REJECTED
        draft.updated_at = datetime.now()
        return await self.draft_repository.update(draft)

    async def delete_draft(self, draft_id: int) -> bool:
        """Delete a recipe draft."""
        return await self.draft_repository.delete(draft_id)

    async def get_draft_stats(self) -> dict[str, Any]:
        """Get statistics about recipe drafts."""
        total = await self.count_drafts()
        draft_count = await self.count_drafts(RecipeDraftStatus.DRAFT)
        validated_count = await self.count_drafts(RecipeDraftStatus.VALIDATED)
        rejected_count = await self.count_drafts(RecipeDraftStatus.REJECTED)

        return {
            "total": total,
            "draft": draft_count,
            "validated": validated_count,
            "rejected": rejected_count,
        }
