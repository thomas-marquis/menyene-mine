"""Use cases for getting resource statistics."""

import asyncio

from ..domain.entities.stats import AppStats, DraftStats, GroceryStats, RecipeStats
from ..domain.ports.grocery_repository import GroceryRepositoryPort
from ..domain.ports.recipe_draft_repository import RecipeDraftRepositoryPort
from ..domain.ports.recipe_repository import RecipeRepositoryPort


class StatsUseCases:
    """Use cases for getting resource statistics."""

    def __init__(
        self,
        recipe_repository: RecipeRepositoryPort,
        draft_repository: RecipeDraftRepositoryPort,
        grocery_repository: GroceryRepositoryPort,
    ) -> None:
        self._recipe_repository = recipe_repository
        self._draft_repository = draft_repository
        self._grocery_repository = grocery_repository

    async def get_all_stats(self) -> AppStats:
        """Get statistics for all resources."""
        recipe_count: int
        draft_stats: DraftStats
        grocery_total: int
        grocery_completed: int

        recipe_count, draft_stats, grocery_total, grocery_completed = await asyncio.gather(
            self._recipe_repository.count_all(),
            self._draft_repository.get_status_counts(),
            self._grocery_repository.count_all(),
            self._grocery_repository.count_by_completed(True),
        )

        grocery_active = grocery_total - grocery_completed

        return AppStats(
            recipes=RecipeStats(total_count=recipe_count),
            drafts=draft_stats,
            groceries=GroceryStats(
                total_count=grocery_total,
                active_count=grocery_active,
                completed_count=grocery_completed,
            ),
        )
