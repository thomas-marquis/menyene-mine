import pytest

from src.domain.entities.recipe import Recipe
from src.services.mock_recipe_generator import MockRecipeAIGenerator
from src.services.recipe_generator import RecipeGenerator


class TestRecipeAIGenerator:
    """Tests for AI Recipe Generator."""

    @pytest.mark.asyncio
    async def test_should_generate_mock_recipe_when_no_api_key(self) -> None:
        # Given
        generator: RecipeGenerator = MockRecipeAIGenerator()

        # When
        recipe = await generator.generate_recipe("Create a pasta recipe")

        # Then
        assert isinstance(recipe, Recipe)
        assert recipe.title is not None
        assert recipe.summary is not None
        assert recipe.ingredients is not None
        assert recipe.instructions is not None

    @pytest.mark.asyncio
    async def test_should_generate_recipe_with_required_fields(self) -> None:
        # Given
        generator: RecipeGenerator = MockRecipeAIGenerator()

        # When
        recipe = await generator.generate_recipe("Create a cake recipe")

        # Then
        assert recipe.title is not None
        assert recipe.summary is not None
        assert recipe.ingredients is not None
        assert recipe.instructions is not None
        assert isinstance(recipe.title, str)
        assert isinstance(recipe.summary, str)
        assert isinstance(recipe.ingredients, list)
        assert isinstance(recipe.instructions, list)

    @pytest.mark.asyncio
    async def test_should_generate_different_recipes_for_different_prompts(self) -> None:
        # Given
        generator: RecipeGenerator = MockRecipeAIGenerator()

        # When
        pasta_recipe = await generator.generate_recipe("Create a pasta recipe")
        salad_recipe = await generator.generate_recipe("Create a salad recipe")

        # Then
        assert isinstance(pasta_recipe, Recipe)
        assert isinstance(salad_recipe, Recipe)
        # Recipes should be different - check multiple fields to reduce flakiness
        assert (
            pasta_recipe.title != salad_recipe.title
            or pasta_recipe.summary != salad_recipe.summary
            or pasta_recipe.ingredients != salad_recipe.ingredients
        )
