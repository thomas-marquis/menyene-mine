import asyncio
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.recipe import Recipe
from ...domain.entities.recipe_draft import RecipeDraft as RecipeDraftEntity
from ...domain.entities.recipe_draft import RecipeDraftContent, RecipeDraftStatus
from ...domain.entities.stats import DraftStats
from ...domain.ports.recipe_draft_repository import RecipeDraftRepositoryPort
from ..models.recipe_draft import RecipeDraft as RecipeDraftModel
from ..models.recipe_draft import RecipeDraftStatus as ModelRecipeDraftStatus


class RecipeDraftRepositoryImpl(RecipeDraftRepositoryPort):
    """SQLAlchemy implementation of RecipeDraft repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, draft: RecipeDraftEntity) -> RecipeDraftEntity:
        """Create a new recipe draft in the database."""
        status_value = ModelRecipeDraftStatus(draft.status.value) if draft.status else ModelRecipeDraftStatus.DRAFT
        content = self._to_dict_content(draft.generated_content)
        draft_model = RecipeDraftModel(
            user_instruction=draft.user_instruction or "",
            generated_content=content or {},
            status=status_value,
            recipe_id=draft.recipe_id,
        )
        self._session.add(draft_model)
        await self._session.commit()
        await self._session.refresh(draft_model)
        return RecipeDraftEntity(
            id=draft_model.id,
            user_instruction=draft_model.user_instruction,
            generated_content=cast(RecipeDraftContent, draft_model.generated_content),
            status=RecipeDraftStatus(draft_model.status),
            created_at=draft_model.created_at,
            updated_at=draft_model.updated_at,
            recipe_id=draft_model.recipe_id,
        )

    async def get_by_id(self, draft_id: int) -> RecipeDraftEntity | None:
        """Get a recipe draft by its ID."""
        result = await self._session.execute(select(RecipeDraftModel).where(RecipeDraftModel.id == draft_id))
        draft_model = result.scalar_one_or_none()
        if draft_model is None:
            return None
        return RecipeDraftEntity(
            id=draft_model.id,
            user_instruction=draft_model.user_instruction,
            generated_content=cast(RecipeDraftContent, draft_model.generated_content),
            status=RecipeDraftStatus(draft_model.status),
            created_at=draft_model.created_at,
            updated_at=draft_model.updated_at,
            recipe_id=draft_model.recipe_id,
        )

    async def update(self, draft: RecipeDraftEntity) -> RecipeDraftEntity | None:
        """Update an existing recipe draft."""
        result = await self._session.execute(select(RecipeDraftModel).where(RecipeDraftModel.id == draft.id))
        draft_model = result.scalar_one_or_none()
        if draft_model is None:
            return None

        if draft.user_instruction is not None:
            draft_model.user_instruction = draft.user_instruction
        if draft.generated_content is not None:
            draft_model.generated_content = dict(self._to_dict_content(draft.generated_content))
        if draft.status is not None:
            draft_model.status = ModelRecipeDraftStatus(draft.status.value)
        if draft.recipe_id is not None:
            draft_model.recipe_id = draft.recipe_id

        await self._session.commit()
        await self._session.refresh(draft_model)
        return RecipeDraftEntity(
            id=draft_model.id,
            user_instruction=draft_model.user_instruction,
            generated_content=cast(RecipeDraftContent, draft_model.generated_content),
            status=RecipeDraftStatus(draft_model.status),
            created_at=draft_model.created_at,
            updated_at=draft_model.updated_at,
            recipe_id=draft_model.recipe_id,
        )

    async def delete(self, draft_id: int) -> bool:
        """Delete a recipe draft by its ID."""
        result = await self._session.execute(select(RecipeDraftModel).where(RecipeDraftModel.id == draft_id))
        draft_model = result.scalar_one_or_none()
        if draft_model is None:
            return False

        await self._session.delete(draft_model)
        await self._session.commit()
        return True

    async def list_all(
        self, skip: int = 0, limit: int = 100, status: RecipeDraftStatus | None = None
    ) -> list[RecipeDraftEntity]:
        """List all recipe drafts with optional status filter and pagination."""
        query = select(RecipeDraftModel).order_by(RecipeDraftModel.created_at.desc())

        if status is not None:
            query = query.where(RecipeDraftModel.status == ModelRecipeDraftStatus(status.value))

        query = query.offset(skip).limit(limit)

        result = await self._session.execute(query)
        drafts = result.scalars().all()
        return [
            RecipeDraftEntity(
                id=r.id,
                user_instruction=r.user_instruction,
                generated_content=cast(RecipeDraftContent, r.generated_content),
                status=RecipeDraftStatus(r.status),
                created_at=r.created_at,
                updated_at=r.updated_at,
                recipe_id=r.recipe_id,
            )
            for r in drafts
        ]

    async def count_by_status(self, status: RecipeDraftStatus | None = None) -> int:
        """Count recipe drafts by status."""
        query = select(func.count(RecipeDraftModel.id))

        if status is not None:
            query = query.where(RecipeDraftModel.status == ModelRecipeDraftStatus(status.value))

        result = await self._session.execute(query)
        return result.scalar_one() or 0

    async def get_status_counts(self) -> DraftStats:
        """Get counts for all draft statuses."""
        draft_count, validated_count, rejected_count = await asyncio.gather(
            self.count_by_status(RecipeDraftStatus.DRAFT),
            self.count_by_status(RecipeDraftStatus.VALIDATED),
            self.count_by_status(RecipeDraftStatus.REJECTED),
        )
        total = draft_count + validated_count + rejected_count
        return DraftStats(
            total_count=total,
            draft_count=draft_count,
            validated_count=validated_count,
            rejected_count=rejected_count,
        )

    def _to_dict_content(self, content: Recipe | RecipeDraftContent | None) -> RecipeDraftContent:
        """
        Convert Recipe entity or dict to dict for database storage.

        Args:
            content: Recipe entity or dict

        Returns:
            Dictionary representation for database storage
        """
        if content is None:
            return {}
        if isinstance(content, Recipe):
            return {
                "title": content.title,
                "summary": content.summary,
                "ingredients": content.ingredients,
                "instructions": content.instructions,
                "servings": content.servings,
                "prep_time": content.prep_time,
                "cook_time": content.cook_time,
                "difficulty": content.difficulty,
            }
        return content
