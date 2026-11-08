from typing import Annotated

from fastapi import Depends

from .domain.ports.grocery_repository import GroceryRepositoryPort
from .domain.ports.recipe_repository import RecipeRepositoryPort
from .infra.db import AsyncSession, get_session
from .infra.repositories.grocery_repository import GroceryRepositoryImpl
from .infra.repositories.recipe_repository import RecipeRepositoryImpl
from .use_cases.grocery_use_cases import GroceryUseCases
from .use_cases.recipe_use_cases import RecipeUseCases

recipe_repository: RecipeRepositoryPort | None = None
recipe_use_cases: RecipeUseCases | None = None
grocery_repository: GroceryRepositoryPort | None = None
grocery_use_cases: GroceryUseCases | None = None


def get_recipe_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RecipeRepositoryPort:
    """Dependency for RecipeRepository."""
    global recipe_repository
    if recipe_repository is None:
        recipe_repository = RecipeRepositoryImpl(session)
    return recipe_repository


def get_recipe_use_cases(
    repository: Annotated[RecipeRepositoryPort, Depends(get_recipe_repository)],
) -> RecipeUseCases:
    """Dependency for RecipeUseCases."""
    global recipe_use_cases
    if recipe_use_cases is None:
        recipe_use_cases = RecipeUseCases(repository)
    return recipe_use_cases


def get_grocery_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GroceryRepositoryPort:
    """Dependency for GroceryRepository."""
    global grocery_repository
    if grocery_repository is None:
        grocery_repository = GroceryRepositoryImpl(session)
    return grocery_repository


def get_grocery_use_cases(
    repository: Annotated[GroceryRepositoryPort, Depends(get_grocery_repository)],
) -> GroceryUseCases:
    """Dependency for GroceryUseCases."""
    global grocery_use_cases
    if grocery_use_cases is None:
        grocery_use_cases = GroceryUseCases(repository)
    return grocery_use_cases


def override_recipe_repository(
    impl: RecipeRepositoryPort,
) -> None:
    """Override dependency for RecipeRepository."""
    global recipe_repository
    recipe_repository = impl


def override_grocery_repository(
    impl: GroceryRepositoryPort,
) -> None:
    """Override dependency for GroceryRepository."""
    global grocery_repository
    grocery_repository = impl
