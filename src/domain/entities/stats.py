from dataclasses import dataclass


@dataclass
class RecipeStats:
    """Recipe statistics domain entity."""

    total_count: int = 0


@dataclass
class DraftStats:
    """Draft statistics domain entity."""

    total_count: int = 0
    draft_count: int = 0
    validated_count: int = 0
    rejected_count: int = 0


@dataclass
class GroceryStats:
    """Grocery statistics domain entity."""

    total_count: int = 0
    active_count: int = 0
    completed_count: int = 0


@dataclass
class AppStats:
    """Application statistics domain entity.

    Aggregates statistics for all main resources in the application.
    """

    recipes: RecipeStats
    drafts: DraftStats
    groceries: GroceryStats
