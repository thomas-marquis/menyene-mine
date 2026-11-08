"""
Abstract base class for AI Recipe Generator service.

This port defines the interface for recipe generation services,
allowing for seamless injection of either mock or real implementations.
"""

from abc import ABC, abstractmethod
from typing import Any


class AIRecipeGeneratorPort(ABC):
    """Abstract base class for AI recipe generators."""

    @abstractmethod
    async def generate_recipes(
        self, prompt: str, max_recipes: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Generate recipe drafts from a user prompt.

        Args:
            prompt: User instruction for recipe generation
            max_recipes: Maximum number of recipes to generate (overrides instance default)

        Returns:
            List of recipe dictionaries with title, content, summary, etc.
        """
        ...
