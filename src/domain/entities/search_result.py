from dataclasses import dataclass

from .recipe import Recipe


@dataclass
class SearchResult:
    """
    Search result domain entity.

    Encapsulates the results of a search operation including the recipes,
    total count, and the search query itself.
    """

    recipes: list[Recipe]
    total: int
    query: str | None = None
    skip: int = 0
    limit: int = 100
