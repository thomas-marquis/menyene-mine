"""
Dependency Injection module.

Centralizes the creation and injection of dependencies throughout the application.
Uses FastAPI's Depends for automatic dependency injection.
"""

from typing import Annotated

from fastapi import Depends
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_mistralai import ChatMistralAI

from .config import get_settings
from .domain.ports.grocery_repository import GroceryRepositoryPort
from .domain.ports.recipe_draft_repository import RecipeDraftRepositoryPort
from .domain.ports.recipe_repository import RecipeRepositoryPort
from .infra.db import AsyncSession, get_session
from .infra.repositories.grocery_repository import GroceryRepositoryImpl
from .infra.repositories.recipe_draft_repository import RecipeDraftRepositoryImpl
from .infra.repositories.recipe_repository import RecipeRepositoryImpl
from .services import MockRecipeAIGenerator, RecipeAIGenerator
from .services.judge import Judge, LLMJudge, MockJudge
from .services.recipe_generator import RecipeGenerator
from .use_cases.grocery_use_cases import GroceryUseCases
from .use_cases.recipe_draft_use_cases import RecipeDraftUseCases
from .use_cases.recipe_generation_workflow import RecipeGenerationWorkflow
from .use_cases.recipe_use_cases import RecipeUseCases

# Global instances for singleton pattern
recipe_repository: RecipeRepositoryPort | None = None
recipe_use_cases: RecipeUseCases | None = None
recipe_draft_repository: RecipeDraftRepositoryPort | None = None
recipe_draft_use_cases: RecipeDraftUseCases | None = None
grocery_repository: GroceryRepositoryPort | None = None
grocery_use_cases: GroceryUseCases | None = None
recipe_generation_workflow: RecipeGenerationWorkflow | None = None
llm: BaseChatModel | None = None


def get_llm() -> BaseChatModel:
    """
    Dependency for ChatMistralAI LLM instance.

    Creates a single instance of ChatMistralAI and reuses it throughout the application.

    Returns:
        BaseChatModel: The LLM instance (ChatMistralAI or mock)
    """

    global llm
    if llm is None:
        settings = get_settings()

        if not settings.mistral_api_key:
            raise RuntimeError("LLM init failed. Please provide a Mistral API key.")

        llm = ChatMistralAI(
            mistral_api_key=settings.mistral_api_key,
            model=settings.ai_model,
            temperature=settings.ai_temperature,
            max_tokens=2000,
        )

    return llm


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


def get_recipe_draft_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RecipeDraftRepositoryPort:
    """Dependency for RecipeDraftRepository."""
    global recipe_draft_repository
    if recipe_draft_repository is None:
        recipe_draft_repository = RecipeDraftRepositoryImpl(session)
    return recipe_draft_repository


def get_ai_recipe_generator() -> RecipeGenerator:
    """
    Dependency for AIRecipeGenerator.

    Creates the appropriate generator based on settings and injects the LLM.

    Returns:
        RecipeGenerator: Either RecipeAIGenerator or MockRecipeAIGenerator
    """

    settings = get_settings()

    if settings.ai_enabled:
        return RecipeAIGenerator(
            llm=get_llm(),
            max_attempts=3,
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

    global recipe_generation_workflow
    if recipe_generation_workflow is None:
        recipe_generation_workflow = RecipeGenerationWorkflow(
            generator=generator,
            judge=judge,
        )
    return recipe_generation_workflow


def get_recipe_draft_use_cases(
    draft_repository: Annotated[RecipeDraftRepositoryPort, Depends(get_recipe_draft_repository)],
    recipe_repository: Annotated[RecipeRepositoryPort, Depends(get_recipe_repository)],
    ai_generator: Annotated[RecipeGenerator, Depends(get_ai_recipe_generator)],
    judge: Annotated[Judge, Depends(get_judge)],
) -> RecipeDraftUseCases:
    """Dependency for RecipeDraftUseCases."""

    global recipe_draft_use_cases
    if recipe_draft_use_cases is None:
        recipe_draft_use_cases = RecipeDraftUseCases(
            draft_repository=draft_repository,
            recipe_repository=recipe_repository,
            recipe_generator=ai_generator,
            judge=judge,
        )
    return recipe_draft_use_cases


def override_recipe_repository(
    impl: RecipeRepositoryPort,
) -> None:
    """Override dependency for RecipeRepository."""
    global recipe_repository
    recipe_repository = impl


def override_recipe_draft_repository(
    impl: RecipeDraftRepositoryPort,
) -> None:
    """Override dependency for RecipeDraftRepository."""
    global recipe_draft_repository
    recipe_draft_repository = impl


def override_grocery_repository(
    impl: GroceryRepositoryPort,
) -> None:
    """Override dependency for GroceryRepository."""
    global grocery_repository
    grocery_repository = impl


def override_llm(
    impl: BaseChatModel,
) -> None:
    """Override dependency for LLM."""
    global llm
    llm = impl
