"""
Abstract base class for Recipe Generator service.

This port defines the interface for recipe generation services,
allowing for seamless injection of either mock or real implementations.
"""

from abc import ABC, abstractmethod

from ..domain.entities.recipe import Recipe


class RecipeGenerator(ABC):
    """Abstract base class for AI recipe generators."""

    @abstractmethod
    async def generate_recipe(self, instructions: str, include_meal_context: bool = True) -> Recipe:
        """
        Generate a single recipe draft from a user prompt.

        Args:
            instructions: User instruction for recipe generation
            include_meal_context: Whether to include recent meal history in the generation context

        Returns:
            Recipe domain entity with title, content, summary, etc.
        """
        ...
