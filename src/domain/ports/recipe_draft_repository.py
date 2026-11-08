from abc import ABC, abstractmethod

from ..entities.recipe_draft import RecipeDraft, RecipeDraftStatus


class RecipeDraftRepositoryPort(ABC):
    """Port interface for RecipeDraft repository."""

    @abstractmethod
    async def create(self, draft: RecipeDraft) -> RecipeDraft:
        """Create a new recipe draft."""
        ...

    @abstractmethod
    async def get_by_id(self, draft_id: int) -> RecipeDraft | None:
        """Get a recipe draft by its ID."""
        ...

    @abstractmethod
    async def update(self, draft: RecipeDraft) -> RecipeDraft | None:
        """Update an existing recipe draft."""
        ...

    @abstractmethod
    async def delete(self, draft_id: int) -> bool:
        """Delete a recipe draft by its ID."""
        ...

    @abstractmethod
    async def list_all(
        self, skip: int = 0, limit: int = 100, status: RecipeDraftStatus | None = None
    ) -> list[RecipeDraft]:
        """List all recipe drafts with optional status filter and pagination."""
        ...

    @abstractmethod
    async def count_by_status(self, status: RecipeDraftStatus | None = None) -> int:
        """Count recipe drafts by status."""
        ...
