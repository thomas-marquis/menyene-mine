"""
Use cases for Recipe Draft operations.
"""

from datetime import datetime
from typing import Any

from ..domain.entities.recipe import Recipe
from ..domain.entities.recipe_draft import RecipeDraft, RecipeDraftContent, RecipeDraftStatus
from ..domain.exceptions import DomainException, InvalidInstructionError
from ..domain.ports.recipe_draft_repository import RecipeDraftRepositoryPort
from ..domain.ports.recipe_repository import RecipeRepositoryPort
from ..services.judge import Judge
from ..services.recipe_generator import RecipeGenerator


class RecipeDraftUseCases:
    """Use cases for RecipeDraft operations."""

    def __init__(
        self,
        draft_repository: RecipeDraftRepositoryPort,
        recipe_repository: RecipeRepositoryPort,
        recipe_generator: RecipeGenerator,
        judge: Judge,
    ) -> None:
        self._draft_repository = draft_repository
        self._recipe_repository = recipe_repository
        self._recipe_generator = recipe_generator
        self._llm_judge = judge

    async def generate_drafts(self, user_instruction: str, max_drafts: int = 10) -> list[RecipeDraft]:
        """
        Generate recipe drafts from a user instruction using AI with LLM validation.

        Args:
            user_instruction: The user's instruction for recipe generation
            max_drafts: Maximum number of drafts to generate (configurable)

        Returns:
            List of created RecipeDraft entities

        Raises:
            InvalidInstructionError: If instruction validation fails
            RecipeGenerationError: If no recipes can be generated
            RecipeValidationError: If no valid recipes can be generated
        """

        try:
            await self._llm_judge.validate_instruction(user_instruction)
        except InvalidInstructionError as e:
            raise InvalidInstructionError(str(e)) from None

        recipe = await self._recipe_generator.generate_recipe(user_instruction)

        if recipe is None:
            raise DomainException("No recipe generated from instruction")

        validated_recipes = [recipe]

        # Create draft for validated recipe
        drafts = []
        for recipe_data in validated_recipes:
            draft = RecipeDraft(
                user_instruction=user_instruction,
                generated_content=recipe_data,
                status=RecipeDraftStatus.DRAFT,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            created_draft = await self._draft_repository.create(draft)
            drafts.append(created_draft)

        return drafts

    async def get_draft(self, draft_id: int) -> RecipeDraft | None:
        """Get a specific recipe draft by ID."""
        return await self._draft_repository.get_by_id(draft_id)

    async def list_drafts(
        self, skip: int = 0, limit: int = 100, status: RecipeDraftStatus | None = None
    ) -> list[RecipeDraft]:
        """List all recipe drafts with optional filtering."""
        return await self._draft_repository.list_all(skip=skip, limit=limit, status=status)

    async def count_drafts(self, status: RecipeDraftStatus | None = None) -> int:
        """Count recipe drafts by status."""
        return await self._draft_repository.count_by_status(status)

    async def validate_draft(self, draft_id: int) -> Recipe | None:
        """
        Validate a draft and create an actual recipe from it.

        Args:
            draft_id: The ID of the draft to validate

        Returns:
            The created Recipe entity, or None if draft not found
        """
        # Get the draft
        draft = await self._draft_repository.get_by_id(draft_id)
        if draft is None:
            return None

        # Extract recipe data from generated content
        if isinstance(draft.generated_content, Recipe):
            recipe_entity = draft.generated_content
            title = recipe_entity.title or "Untitled Recipe"
            summary = recipe_entity.summary or ""
            ingredients = recipe_entity.ingredients or []
            instructions = recipe_entity.instructions or []
            servings = recipe_entity.servings or 4
            prep_time = recipe_entity.prep_time or "0 minutes"
            cook_time = recipe_entity.cook_time or "0 minutes"
            difficulty = recipe_entity.difficulty or "Medium"
        else:
            content: RecipeDraftContent = draft.generated_content or {}
            title = content.get("title") or "Untitled Recipe"
            summary = content.get("summary") or ""
            ingredients = content.get("ingredients") or []
            instructions = content.get("instructions") or []
            servings = content.get("servings") or 4
            prep_time = content.get("prep_time") or "0 minutes"
            cook_time = content.get("cook_time") or "0 minutes"
            difficulty = content.get("difficulty") or "Medium"

        # Create the actual recipe
        recipe = Recipe(
            title=title,
            summary=summary,
            ingredients=ingredients,
            instructions=instructions,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
            difficulty=difficulty,
        )
        created_recipe = await self._recipe_repository.create(recipe)

        # Update the draft to mark it as validated and link to the recipe
        draft.status = RecipeDraftStatus.VALIDATED
        draft.recipe_id = created_recipe.id
        draft.updated_at = datetime.now()
        await self._draft_repository.update(draft)

        return created_recipe

    async def reject_draft(self, draft_id: int) -> RecipeDraft | None:
        """
        Reject a draft.

        Args:
            draft_id: The ID of the draft to reject

        Returns:
            The updated RecipeDraft entity, or None if not found
        """
        draft = await self._draft_repository.get_by_id(draft_id)
        if draft is None:
            return None

        draft.status = RecipeDraftStatus.REJECTED
        draft.updated_at = datetime.now()
        return await self._draft_repository.update(draft)

    async def delete_draft(self, draft_id: int) -> bool:
        """Delete a recipe draft."""
        return await self._draft_repository.delete(draft_id)

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
