"""
AI Recipe Generator Service Implementation

This service uses LangChain with Mistral to generate recipes from user instructions.
Templates are loaded from the config directory.
"""

import asyncio
from datetime import date, timedelta

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from ..config import get_prompt_loader
from ..domain.entities.recipe import Recipe
from ..domain.exceptions import RecipeGenerationError
from ..domain.ports.meal_repository import MealRepositoryPort
from ..domain.ports.recipe_repository import RecipeRepositoryPort
from .recipe_generator import RecipeGenerator
from .recipe_models import GeneratedRecipe


class RecipeGenerationState(BaseModel):
    """State for the recipe generation retry workflow."""

    instruction: str
    recent_meals: list[Recipe] | None = None
    attempts: int = 0
    max_attempts: int = 3
    error: str | None = None
    recipe: GeneratedRecipe | None = None


class RecipeAIGenerator(RecipeGenerator):
    """
    Production AI recipe generator service.

    Uses LangChain with Mistral to generate recipes from Jinja2 templates.
    Implements a retry mechanism with LangGraph for robust generation.
    Supports optional meal history context for more intelligent recipe suggestions.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        meal_repository: MealRepositoryPort,
        recipe_repository: RecipeRepositoryPort,
        max_attempts: int = 3,
    ):
        """
        Initialize the AI recipe generator.

        Args:
            llm: The LLM instance to use
            max_attempts: Maximum number of generation attempts before failing
            meal_repository: Repository for fetching meal history
            recipe_repository: Repository for fetching recipe details
        """
        self._llm = llm
        self._max_attempts = max_attempts
        self._meal_repository = meal_repository
        self._recipe_repository = recipe_repository

        # Load templates in constructor
        prompt_loader = get_prompt_loader()
        self._system_template = prompt_loader.load("system")
        self._generation_template = prompt_loader.load("recipe_generation")
        self._instruction_validation_template = prompt_loader.load("instruction_validation")

        self._build_generator_workflow()

    async def generate_recipe(self, instructions: str, include_meal_context: bool = True) -> Recipe:
        """
        Generate a single recipe draft from a user instruction.

        Args:
            instructions: User instruction for recipe generation
            include_meal_context: Whether to include recent meal history in the context (default: True)

        Returns:
            Recipe domain entity with title, content, summary, etc.

        Raises:
            RecipeGenerationError: If recipe generation fails after all retry attempts
            Exception: If meal context fetching fails and include_meal_context is True
        """

        recent_meals = []
        if include_meal_context:
            recent_meals = await self._get_recent_meals(days=7)

        initial_state = RecipeGenerationState(
            instruction=instructions,
            recent_meals=recent_meals,
            max_attempts=self._max_attempts,
        )

        final_state_dict = await self._workflow.ainvoke(initial_state)

        final_state = RecipeGenerationState(**final_state_dict)

        if final_state.recipe is not None:
            return self._to_domain_entity(final_state.recipe)
        else:
            error_msg = final_state.error or "Failed to generate recipe after multiple attempts"
            raise RecipeGenerationError(error_msg) from None

    async def _get_recent_meals(self, days: int = 7) -> list[Recipe]:
        """
        Fetch recent meal history as Recipe entities for use as AI context.

        Args:
            days: Number of past days to include in the context

        Returns:
            List of Recipe entities for recent meals, or empty list if none found

        Raises:
            Exception: If database error occurs while fetching meals or recipes
        """

        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        meals = await self._meal_repository.get_meals_for_date_range(start_date, end_date, unique_recipes=True)

        coros = [self._recipe_repository.get_by_id(meal.recipe_id) for meal in meals if meal.recipe_id]
        recipes = await asyncio.gather(*coros)

        return [r for r in recipes if r]

    def _to_domain_entity(self, recipe: GeneratedRecipe) -> Recipe:
        """
        Convert a Pydantic GeneratedRecipe model to a Recipe domain entity.

        Args:
            recipe: Pydantic GeneratedRecipe model

        Returns:
            Recipe domain entity with structured fields
        """

        return Recipe(
            title=recipe.title,
            summary=recipe.summary,
            ingredients=recipe.ingredients,
            instructions=recipe.instructions,
            servings=recipe.servings,
            prep_time=recipe.prep_time,
            cook_time=recipe.cook_time,
            difficulty=recipe.difficulty,
        )

    def _build_generator_workflow(self) -> None:
        """Build the LangGraph retry workflow for recipe generation."""

        builder = StateGraph(RecipeGenerationState)

        builder.add_node("generate", self._generate_node)
        builder.add_node("validate", self._validate_node)

        builder.add_edge(START, "generate")
        builder.add_edge("generate", "validate")

        builder.add_conditional_edges(
            "validate",
            self._should_retry,
            {
                "retry": "generate",
                "success": END,
                "failure": END,
            },
        )

        self._workflow = builder.compile()

    async def _generate_node(self, state: RecipeGenerationState) -> RecipeGenerationState:
        """
        Generate a recipe using AI.

        Args:
            state: Current workflow state

        Returns:
            Updated state with generated recipe or error
        """

        try:
            system_prompt = self._system_template.render()
            generation_prompt = self._generation_template.render(
                instruction=state.instruction,
                recent_meals=state.recent_meals or [],
            )

            messages: list[BaseMessage] = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=generation_prompt),
            ]

            llm_with_structured_output = self._llm.with_structured_output(GeneratedRecipe)

            response = await llm_with_structured_output.ainvoke(messages)
            recipe: GeneratedRecipe = response  # type: ignore[assignment]

            return RecipeGenerationState(
                instruction=state.instruction,
                recent_meals=state.recent_meals,
                attempts=state.attempts + 1,
                max_attempts=state.max_attempts,
                error=None,
                recipe=recipe,
            )
        except Exception as e:
            return RecipeGenerationState(
                instruction=state.instruction,
                recent_meals=state.recent_meals,
                attempts=state.attempts + 1,
                max_attempts=state.max_attempts,
                error=str(e),
                recipe=None,
            )

    def _validate_node(self, state: RecipeGenerationState) -> RecipeGenerationState:
        """
        Validate the generated recipe.

        Args:
            state: Current workflow state

        Returns:
            Updated state with validation result
        """
        if state.recipe is not None:
            return state
        else:
            return RecipeGenerationState(
                instruction=state.instruction,
                recent_meals=state.recent_meals,
                attempts=state.attempts,
                max_attempts=state.max_attempts,
                error=state.error or "No recipe generated",
                recipe=None,
            )

    def _should_retry(self, state: RecipeGenerationState) -> str:
        """
        Determine if we should retry generation.

        Args:
            state: Current workflow state

        Returns:
            "retry" if we should try again, "success" if successful,
            "failure" if max attempts reached
        """
        if state.recipe is not None:
            return "success"
        elif state.attempts >= state.max_attempts:
            return "failure"
        else:
            return "retry"
