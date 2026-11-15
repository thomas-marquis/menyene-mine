"""
Recipe Generation Workflow using LangGraph.

This module implements a LangGraph workflow for AI-powered recipe generation
with validation using LLM Judge.
"""

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from ..config import Settings, get_prompt_loader, get_settings
from ..domain.entities.recipe import Recipe
from ..domain.exceptions import DomainException, InvalidInstructionError
from ..services.judge import Judge
from ..services.recipe_generator import RecipeGenerator


class RecipeGenerationState(TypedDict, total=False):
    """State for the recipe generation workflow."""

    instruction: str
    validated_instruction: bool | None
    instruction_error: str | None
    recipe: Recipe | None
    error: str | None


class RecipeGenerationWorkflow:
    """
    LangGraph workflow for recipe generation with validation.

    This workflow:
    1. Validates the user instruction using LLM Judge
    2. Generates a recipe using AI Generator
    3. Returns the generated recipe or errors

    For v1: Generates exactly ONE recipe
    """

    def __init__(
        self,
        generator: RecipeGenerator,
        judge: Judge,
    ):
        """
        Initialize the recipe generation workflow.

        Args:
            generator: Recipe generator service
            judge: Judge service for validation
        """

        self._settings = get_settings()
        self._judge: Judge
        self._generator = generator
        self._judge = judge

        self._template_loader = get_prompt_loader()
        self._build_workflow()

    @property
    def generator(self) -> RecipeGenerator:
        """Get the recipe generator."""
        return self._generator

    @property
    def judge(self) -> Judge:
        """Get the judge service."""
        return self._judge

    @property
    def settings(self) -> Settings:
        """Get the settings (for backward compatibility)."""
        return self._settings

    @property
    def template_loader(self) -> Any:
        """Get the template loader (for backward compatibility)."""
        return self._template_loader

    def _build_workflow(self) -> None:
        """Build the LangGraph workflow."""
        builder = StateGraph(RecipeGenerationState)

        builder.add_node("validate_instruction", self._validate_instruction_node)
        builder.add_node("generate_recipe", self._generate_recipe_node)

        builder.add_conditional_edges(
            "validate_instruction",
            self._should_continue_instruction_validation,
            {
                "continue": "generate_recipe",
                "error": END,
            },
        )

        builder.set_entry_point("validate_instruction")

        self._workflow = builder.compile()

    async def _validate_instruction_node(self, state: RecipeGenerationState) -> RecipeGenerationState:
        """
        Validate the user instruction using LLM Judge.

        Args:
            state: Current workflow state

        Returns:
            Updated state with validation result
        """
        try:
            await self._judge.validate_instruction(state["instruction"])

            return {
                **state,
                "validated_instruction": True,
                "instruction_error": None,
            }
        except InvalidInstructionError as e:
            return {
                **state,
                "validated_instruction": False,
                "instruction_error": str(e),
            }
        except Exception as e:
            return {
                **state,
                "validated_instruction": False,
                "instruction_error": f"Instruction validation failed: {str(e)}",
            }

    def _should_continue_instruction_validation(self, state: RecipeGenerationState) -> str:
        """
        Determine if workflow should continue after instruction validation.

        Args:
            state: Current workflow state

        Returns:
            "continue" if validation passed, "error" otherwise
        """
        if state.get("validated_instruction") is True:
            return "continue"
        return "error"

    async def _generate_recipe_node(self, state: RecipeGenerationState) -> RecipeGenerationState:
        """
        Generate a recipe using AI Generator.

        Args:
            state: Current workflow state

        Returns:
            Updated state with generated recipe
        """
        try:
            # For v1, generate exactly 1 recipe
            recipe = await self._generator.generate_recipe(state["instruction"])

            if recipe is None:
                return {
                    **state,
                    "error": "No recipe generated from instruction",
                }

            return {
                **state,
                "recipe": recipe,
            }
        except DomainException as e:
            return {
                **state,
                "error": str(e),
            }
        except Exception as e:
            return {
                **state,
                "error": f"Recipe generation failed: {str(e)}",
            }

    async def generate_recipe(self, instruction: str) -> dict[str, Any]:
        """
        Generate a recipe using the LangGraph workflow.

        Args:
            instruction: User instruction for recipe generation

        Returns:
            Dictionary with:
            - success: bool indicating if generation was successful
            - recipe: Generated recipe (if successful)
            - error: Error message (if failed)
            - instruction_error: Instruction validation error (if any)
        """
        initial_state: RecipeGenerationState = {"instruction": instruction}

        try:
            final_state = await self._workflow.ainvoke(initial_state)

            result: dict[str, Any] = {
                "success": final_state.get("recipe") is not None,
                "recipe": final_state.get("recipe"),
            }

            # Add errors if any
            if final_state.get("instruction_error"):
                result["instruction_error"] = final_state["instruction_error"]

            if final_state.get("error"):
                result["error"] = final_state["error"]

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def generate_and_validate(self, instruction: str) -> tuple[bool, dict[str, Any] | None, str | None]:
        """
        Generate and validate a recipe, returning a tuple.

        Args:
            instruction: User instruction for recipe generation

        Returns:
            Tuple of (success, recipe, error)
        """
        result = await self.generate_recipe(instruction)

        if result.get("success"):
            return True, result.get("recipe"), None
        else:
            return False, None, result.get("error") or result.get("instruction_error")
