# REST controllers
from .meal_routes import router as meal_routes
from .recipe_routes import router as recipe_routes

__all__ = ["recipe_routes", "meal_routes"]
