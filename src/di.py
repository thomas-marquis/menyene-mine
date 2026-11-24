"""
Dependency Injection module.

Centralizes the creation and injection of dependencies throughout the application.
Uses FastAPI's Depends for automatic dependency injection.
"""

from contextvars import ContextVar
from typing import Annotated

from fastapi import Depends
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_mistralai import ChatMistralAI

from .config import get_settings
from .domain.ports.grocery_repository import GroceryRepositoryPort
from .domain.ports.meal_repository import MealRepositoryPort
from .domain.ports.recipe_draft_repository import RecipeDraftRepositoryPort
from .domain.ports.recipe_repository import RecipeRepositoryPort
from .infra.db import AsyncSession, get_session
from .infra.repositories.grocery_repository import GroceryRepositoryImpl
from .infra.repositories.meal_repository import MealRepositoryImpl
from .infra.repositories.recipe_draft_repository import RecipeDraftRepositoryImpl
from .infra.repositories.recipe_repository import RecipeRepositoryImpl
from .services import MockRecipeAIGenerator, RecipeAIGenerator
from .services.judge import Judge, LLMJudge, MockJudge
from .services.recipe_generator import RecipeGenerator
from .use_cases.grocery_use_cases import GroceryUseCases
from .use_cases.meal_use_cases import MealUseCases
from .use_cases.recipe_draft_use_cases import RecipeDraftUseCases
from .use_cases.recipe_generation_workflow import RecipeGenerationWorkflow
from .use_cases.recipe_use_cases import RecipeUseCases
from .use_cases.stats_use_cases import StatsUseCases

# Global instances for singleton pattern
_recipe_repository: ContextVar[RecipeRepositoryPort | None] = ContextVar("recipe_repository", default=None)
_recipe_use_cases: ContextVar[RecipeUseCases | None] = ContextVar("recipe_use_cases", default=None)
_recipe_draft_repository: ContextVar[RecipeDraftRepositoryPort | None] = ContextVar(
    "recipe_draft_repository", default=None
)
_recipe_draft_use_cases: ContextVar[RecipeDraftUseCases | None] = ContextVar("recipe_draft_use_cases", default=None)
_grocery_repository: ContextVar[GroceryRepositoryPort | None] = ContextVar("grocery_repository", default=None)
_grocery_use_cases: ContextVar[GroceryUseCases | None] = ContextVar("grocery_use_cases", default=None)
_meal_repository: ContextVar[MealRepositoryPort | None] = ContextVar("meal_repository", default=None)
_meal_use_cases: ContextVar[MealUseCases | None] = ContextVar("meal_use_cases", default=None)
_stats_use_cases: ContextVar[StatsUseCases | None] = ContextVar("stats_use_cases", default=None)
_recipe_generation_workflow: ContextVar[RecipeGenerationWorkflow | None] = ContextVar(
    "recipe_generation_workflow", default=None
)
_llm: ContextVar[BaseChatModel | None] = ContextVar("llm", default=None)


def get_llm() -> BaseChatModel:
    """
    Dependency for ChatMistralAI LLM instance.

    Creates a single instance of ChatMistralAI and reuses it throughout the application.

    Returns:
        BaseChatModel: The LLM instance (ChatMistralAI or mock)
    """

    if _llm.get() is None:
        settings = get_settings()

        if not settings.mistral_api_key:
            raise RuntimeError("LLM init failed. Please provide a Mistral API key.")

        _llm.set(
            ChatMistralAI(
                mistral_api_key=settings.mistral_api_key,
                model=settings.ai_model,
                temperature=settings.ai_temperature,
                max_tokens=2000,
            )
        )

    return _llm.get()  # type: ignore


def get_recipe_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RecipeRepositoryPort:
    """Dependency for RecipeRepository."""
    if _recipe_repository.get() is None:
        _recipe_repository.set(RecipeRepositoryImpl(session))
    return _recipe_repository.get()  # type: ignore


def get_recipe_use_cases(
    repository: Annotated[RecipeRepositoryPort, Depends(get_recipe_repository)],
) -> RecipeUseCases:
    """Dependency for RecipeUseCases."""
    if _recipe_use_cases.get() is None:
        _recipe_use_cases.set(RecipeUseCases(repository))
    return _recipe_use_cases.get()  # type: ignore


def get_grocery_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GroceryRepositoryPort:
    """Dependency for GroceryRepository."""
    if _grocery_repository.get() is None:
        _grocery_repository.set(GroceryRepositoryImpl(session))
    return _grocery_repository.get()  # type: ignore


def get_grocery_use_cases(
    repository: Annotated[GroceryRepositoryPort, Depends(get_grocery_repository)],
) -> GroceryUseCases:
    """Dependency for GroceryUseCases."""
    if _grocery_use_cases.get() is None:
        _grocery_use_cases.set(GroceryUseCases(repository))
    return _grocery_use_cases.get()  # type: ignore


def get_meal_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MealRepositoryPort:
    """Dependency for MealRepository."""
    if _meal_repository.get() is None:
        _meal_repository.set(MealRepositoryImpl(session))
    return _meal_repository.get()  # type: ignore


def get_meal_use_cases(
    meal_repository: Annotated[MealRepositoryPort, Depends(get_meal_repository)],
    recipe_repository: Annotated[RecipeRepositoryPort, Depends(get_recipe_repository)],
) -> MealUseCases:
    """Dependency for MealUseCases."""
    if _meal_use_cases.get() is None:
        _meal_use_cases.set(MealUseCases(meal_repository, recipe_repository))
    return _meal_use_cases.get()  # type: ignore


def get_recipe_draft_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RecipeDraftRepositoryPort:
    """Dependency for RecipeDraftRepository."""
    if _recipe_draft_repository.get() is None:
        _recipe_draft_repository.set(RecipeDraftRepositoryImpl(session))
    return _recipe_draft_repository.get()  # type: ignore


def get_stats_use_cases(
    recipe_repository: Annotated[RecipeRepositoryPort, Depends(get_recipe_repository)],
    draft_repository: Annotated[RecipeDraftRepositoryPort, Depends(get_recipe_draft_repository)],
    grocery_repository: Annotated[GroceryRepositoryPort, Depends(get_grocery_repository)],
) -> StatsUseCases:
    """Dependency for StatsUseCases."""
    if _stats_use_cases.get() is None:
        _stats_use_cases.set(
            StatsUseCases(
                recipe_repository=recipe_repository,
                draft_repository=draft_repository,
                grocery_repository=grocery_repository,
            )
        )
    return _stats_use_cases.get()  # type: ignore


def get_ai_recipe_generator(
    meal_repository: Annotated[MealRepositoryPort, Depends(get_meal_repository)],
    recipe_repository: Annotated[RecipeRepositoryPort, Depends(get_recipe_repository)],
) -> RecipeGenerator:
    """
    Dependency for AIRecipeGenerator.

    Creates the appropriate generator based on settings and injects the LLM and repositories.

    Args:
        meal_repository: Meal repository for fetching meal history
        recipe_repository: Recipe repository for fetching recipe details

    Returns:
        RecipeGenerator: Either RecipeAIGenerator or MockRecipeAIGenerator
    """

    settings = get_settings()

    if settings.ai_enabled:
        return RecipeAIGenerator(
            llm=get_llm(),
            max_attempts=3,
            meal_repository=meal_repository,
            recipe_repository=recipe_repository,
        )

    return MockRecipeAIGenerator()


def get_judge() -> Judge:
    """
    Dependency for Judge service.

    Creates the LLM Judge or Mock Judge based on AI settings.

    Returns:
        Judge: The judge service (LLMJudge or MockJudge)
    """

    settings = get_settings()

    if settings.ai_enabled:
        return LLMJudge(llm=get_llm())
    else:
        return MockJudge()


def get_recipe_generation_workflow(
    generator: Annotated[RecipeGenerator, Depends(get_ai_recipe_generator)],
    judge: Annotated[Judge, Depends(get_judge)],
) -> RecipeGenerationWorkflow:
    """
    Dependency for RecipeGenerationWorkflow.

    Creates the workflow with injected generator and judge.

    Args:
        generator: The recipe generator service
        judge: The LLM judge service

    Returns:
        RecipeGenerationWorkflow: The workflow with injected dependencies
    """

    if _recipe_generation_workflow.get() is None:
        _recipe_generation_workflow.set(
            RecipeGenerationWorkflow(
                generator=generator,
                judge=judge,
            )
        )
    return _recipe_generation_workflow.get()  # type: ignore


def get_recipe_draft_use_cases(
    draft_repository: Annotated[RecipeDraftRepositoryPort, Depends(get_recipe_draft_repository)],
    recipe_repository: Annotated[RecipeRepositoryPort, Depends(get_recipe_repository)],
    ai_generator: Annotated[RecipeGenerator, Depends(get_ai_recipe_generator)],
    judge: Annotated[Judge, Depends(get_judge)],
) -> RecipeDraftUseCases:
    """Dependency for RecipeDraftUseCases."""

    if _recipe_draft_use_cases.get() is None:
        _recipe_draft_use_cases.set(
            RecipeDraftUseCases(
                draft_repository=draft_repository,
                recipe_repository=recipe_repository,
                recipe_generator=ai_generator,
                judge=judge,
            )
        )
    return _recipe_draft_use_cases.get()  # type: ignore


def override_recipe_repository(
    impl: RecipeRepositoryPort,
) -> None:
    """Override dependency for RecipeRepository."""
    _recipe_repository.set(impl)


def override_recipe_draft_repository(
    impl: RecipeDraftRepositoryPort,
) -> None:
    """Override dependency for RecipeDraftRepository."""
    _recipe_draft_repository.set(impl)


def override_grocery_repository(
    impl: GroceryRepositoryPort,
) -> None:
    """Override dependency for GroceryRepository."""
    _grocery_repository.set(impl)


def override_meal_repository(
    impl: MealRepositoryPort,
) -> None:
    """Override dependency for MealRepository."""
    _meal_repository.set(impl)


def override_llm(
    impl: BaseChatModel,
) -> None:
    """Override dependency for LLM."""
    _llm.set(impl)
