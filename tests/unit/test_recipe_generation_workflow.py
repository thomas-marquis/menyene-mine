"""
Unit tests for the recipe generation workflow.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.entities.recipe import Recipe
from src.domain.exceptions import InvalidInstructionError, RecipeValidationError
from src.services.judge import LLMJudge
from src.services.recipe_generator import RecipeGenerator
from src.use_cases.recipe_generation_workflow import (
    RecipeGenerationState,
    RecipeGenerationWorkflow,
)


@pytest.fixture
def mock_llm_judge() -> MagicMock:
    """Create a MagicMock for LLMJudge with async methods."""
    mock = MagicMock(spec=LLMJudge)

    # Mock validate_instruction to return None (success)
    mock.validate_instruction = AsyncMock(return_value=None)

    # Mock validate_recipe to return None (success)
    mock.validate_recipe = AsyncMock(return_value=None)

    return mock


@pytest.fixture
def mock_llm_judge_with_errors() -> MagicMock:
    """Create a MagicMock for LLMJudge that raises exceptions."""
    mock = MagicMock(spec=LLMJudge)

    # Mock validate_instruction to raise InvalidInstructionError
    mock.validate_instruction = AsyncMock(side_effect=InvalidInstructionError("Invalid instruction"))

    # Mock validate_recipe to raise RecipeValidationError
    mock.validate_recipe = AsyncMock(side_effect=RecipeValidationError("Invalid recipe", ["missing ingredients"]))

    return mock


@pytest.fixture
def mock_recipe_generator() -> MagicMock:
    """Create a MagicMock for RecipeGenerator."""
    mock = MagicMock(spec=RecipeGenerator)

    # Mock generate_recipe to return a simple recipe
    mock.generate_recipe = AsyncMock(
        return_value=Recipe(
            title="Test Recipe",
            content="Test content",
            summary="Test summary",
        )
    )

    return mock


@pytest.fixture
def mock_recipe_generator_empty() -> MagicMock:
    """Create a MagicMock for RecipeGenerator that returns None."""
    mock = MagicMock(spec=RecipeGenerator)

    # Mock generate_recipe to return None
    mock.generate_recipe = AsyncMock(return_value=None)

    return mock


@pytest.fixture
def mock_workflow(mock_recipe_generator: MagicMock, mock_llm_judge: MagicMock) -> RecipeGenerationWorkflow:
    """Create a workflow with mocked generator and judge using pytest fixtures."""
    with patch("src.use_cases.recipe_generation_workflow.get_settings") as mock_settings:
        mock_settings.return_value.ai_enabled = False
        mock_settings.return_value.mistral_api_key = None

        workflow = RecipeGenerationWorkflow(
            generator=mock_recipe_generator,
            judge=mock_llm_judge,
        )

        return workflow


@pytest.fixture
def mock_workflow_with_validation_error(
    mock_recipe_generator: MagicMock, mock_llm_judge_with_errors: MagicMock
) -> RecipeGenerationWorkflow:
    """Create a workflow with mocked generator and judge that raises validation errors."""
    with patch("src.use_cases.recipe_generation_workflow.get_settings") as mock_settings:
        mock_settings.return_value.ai_enabled = False
        mock_settings.return_value.mistral_api_key = None

        workflow = RecipeGenerationWorkflow(
            generator=mock_recipe_generator,
            judge=mock_llm_judge_with_errors,
        )

        return workflow


@pytest.fixture
def mock_workflow_with_generation_error(
    mock_recipe_generator_empty: MagicMock, mock_llm_judge: MagicMock
) -> RecipeGenerationWorkflow:
    """Create a workflow with empty generator."""
    with patch("src.use_cases.recipe_generation_workflow.get_settings") as mock_settings:
        mock_settings.return_value.ai_enabled = False
        mock_settings.return_value.mistral_api_key = None

        workflow = RecipeGenerationWorkflow(
            generator=mock_recipe_generator_empty,
            judge=mock_llm_judge,
        )

        return workflow


class TestRecipeGenerationWorkflow:
    """Tests for RecipeGenerationWorkflow."""

    @pytest.mark.asyncio
    async def test_generate_recipe_with_mock(self, mock_workflow: RecipeGenerationWorkflow) -> None:
        """Test recipe generation with mock generator."""
        result = await mock_workflow.generate_recipe("Make a chocolate cake")

        assert "success" in result
        assert result["success"] is True
        assert "recipe" in result
        assert result["recipe"] is not None

        # Check that recipe has expected fields
        recipe = result["recipe"]
        assert recipe.title is not None
        assert recipe.content is not None
        assert recipe.summary is not None

    @pytest.mark.asyncio
    async def test_generate_and_validate_success(self, mock_workflow: RecipeGenerationWorkflow) -> None:
        """Test the generate_and_validate method with successful generation."""
        success, recipe, error = await mock_workflow.generate_and_validate("Make a pasta dish")

        assert success is True
        assert recipe is not None
        assert isinstance(recipe, Recipe)
        assert error is None

    @pytest.mark.asyncio
    async def test_generate_recipe_with_instruction_validation_error(
        self, mock_workflow_with_validation_error: RecipeGenerationWorkflow
    ) -> None:
        """Test recipe generation with instruction validation errors."""
        result = await mock_workflow_with_validation_error.generate_recipe("Invalid instruction")

        assert "success" in result
        assert result["success"] is False
        assert "instruction_error" in result
        assert result["instruction_error"] is not None

    @pytest.mark.asyncio
    async def test_generate_and_validate_with_instruction_error(
        self, mock_workflow_with_validation_error: RecipeGenerationWorkflow
    ) -> None:
        """Test generate_and_validate with instruction validation errors."""
        success, recipe, error = await mock_workflow_with_validation_error.generate_and_validate("Invalid instruction")

        assert success is False
        assert recipe is None
        assert error is not None

    @pytest.mark.asyncio
    async def test_generate_recipe_with_generation_error(
        self, mock_workflow_with_generation_error: RecipeGenerationWorkflow
    ) -> None:
        """Test recipe generation with generation errors."""
        result = await mock_workflow_with_generation_error.generate_recipe("Make a cake")

        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert result["error"] is not None

    def test_state_typeddict(self) -> None:
        """Test that RecipeGenerationState is a proper TypedDict."""
        state: RecipeGenerationState = {
            "instruction": "Make a cake",
            "validated_instruction": True,
            "instruction_error": None,
            "generated_recipes": [],
            "validated_recipes": [],
            "recipe_errors": [],
            "final_recipe": None,
            "error": None,
        }

        assert state["instruction"] == "Make a cake"
        assert state["validated_instruction"] is True


class TestRecipeGenerationState:
    """Tests for RecipeGenerationState TypedDict."""

    def test_state_creation(self) -> None:
        """Test creating a state dict."""
        state: RecipeGenerationState = {
            "instruction": "Make a recipe",
        }

        assert state["instruction"] == "Make a recipe"

    def test_state_with_all_fields(self) -> None:
        """Test state with all fields."""
        recipe = Recipe(title="Test", content="Test content", summary="Test summary")
        state: RecipeGenerationState = {
            "instruction": "Make a test",
            "validated_instruction": True,
            "instruction_error": None,
            "generated_recipes": [recipe],
            "validated_recipes": [recipe],
            "recipe_errors": [],
            "final_recipe": recipe,
            "error": None,
        }

        assert state["instruction"] == "Make a test"
        assert state["validated_instruction"] is True
        assert state["generated_recipes"] == [recipe]
        assert state["final_recipe"] == recipe
