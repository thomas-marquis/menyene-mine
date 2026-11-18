# Domain ports (interfaces)
from .meal_repository import MealRepositoryPort
from .recipe_repository import RecipeRepositoryPort

__all__ = ["RecipeRepositoryPort", "MealRepositoryPort"]
