from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.recipe_draft import RecipeDraft as RecipeDraftEntity
from ...domain.entities.recipe_draft import RecipeDraftStatus
from ...domain.ports.recipe_draft_repository import RecipeDraftRepositoryPort
from ..models.recipe_draft import RecipeDraft as RecipeDraftModel
from ..models.recipe_draft import RecipeDraftStatus as ModelRecipeDraftStatus


class RecipeDraftRepositoryImpl(RecipeDraftRepositoryPort):
    """SQLAlchemy implementation of RecipeDraft repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, draft: RecipeDraftEntity) -> RecipeDraftEntity:
        """Create a new recipe draft in the database."""
        status_value = (
            ModelRecipeDraftStatus(draft.status.value)
            if draft.status
            else ModelRecipeDraftStatus.DRAFT
        )
        draft_model = RecipeDraftModel(
            user_prompt=draft.user_prompt or "",
            generated_content=draft.generated_content or {},
            status=status_value,
            recipe_id=draft.recipe_id,
        )
        self.session.add(draft_model)
        await self.session.commit()
        await self.session.refresh(draft_model)
        return RecipeDraftEntity(
            id=draft_model.id,
            user_prompt=draft_model.user_prompt,
            generated_content=draft_model.generated_content,
            status=RecipeDraftStatus(draft_model.status),
            created_at=draft_model.created_at,
            updated_at=draft_model.updated_at,
            recipe_id=draft_model.recipe_id,
        )

    async def get_by_id(self, draft_id: int) -> RecipeDraftEntity | None:
        """Get a recipe draft by its ID."""
        result = await self.session.execute(
            select(RecipeDraftModel).where(RecipeDraftModel.id == draft_id)
        )
        draft_model = result.scalar_one_or_none()
        if draft_model is None:
            return None
        return RecipeDraftEntity(
            id=draft_model.id,
            user_prompt=draft_model.user_prompt,
            generated_content=draft_model.generated_content,
            status=RecipeDraftStatus(draft_model.status),
            created_at=draft_model.created_at,
            updated_at=draft_model.updated_at,
            recipe_id=draft_model.recipe_id,
        )

    async def update(self, draft: RecipeDraftEntity) -> RecipeDraftEntity | None:
        """Update an existing recipe draft."""
        result = await self.session.execute(
            select(RecipeDraftModel).where(RecipeDraftModel.id == draft.id)
        )
        draft_model = result.scalar_one_or_none()
        if draft_model is None:
            return None

        if draft.user_prompt is not None:
            draft_model.user_prompt = draft.user_prompt
        if draft.generated_content is not None:
            draft_model.generated_content = draft.generated_content
        if draft.status is not None:
            draft_model.status = ModelRecipeDraftStatus(draft.status.value)
        if draft.recipe_id is not None:
            draft_model.recipe_id = draft.recipe_id

        await self.session.commit()
        await self.session.refresh(draft_model)
        return RecipeDraftEntity(
            id=draft_model.id,
            user_prompt=draft_model.user_prompt,
            generated_content=draft_model.generated_content,
            status=RecipeDraftStatus(draft_model.status),
            created_at=draft_model.created_at,
            updated_at=draft_model.updated_at,
            recipe_id=draft_model.recipe_id,
        )

    async def delete(self, draft_id: int) -> bool:
        """Delete a recipe draft by its ID."""
        result = await self.session.execute(
            select(RecipeDraftModel).where(RecipeDraftModel.id == draft_id)
        )
        draft_model = result.scalar_one_or_none()
        if draft_model is None:
            return False

        await self.session.delete(draft_model)
        await self.session.commit()
        return True

    async def list_all(
        self, skip: int = 0, limit: int = 100, status: RecipeDraftStatus | None = None
    ) -> list[RecipeDraftEntity]:
        """List all recipe drafts with optional status filter and pagination."""
        query = select(RecipeDraftModel).order_by(RecipeDraftModel.created_at.desc())

        if status is not None:
            query = query.where(RecipeDraftModel.status == ModelRecipeDraftStatus(status.value))

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        drafts = result.scalars().all()
        return [
            RecipeDraftEntity(
                id=r.id,
                user_prompt=r.user_prompt,
                generated_content=r.generated_content,
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

        result = await self.session.execute(query)
        return result.scalar_one() or 0
