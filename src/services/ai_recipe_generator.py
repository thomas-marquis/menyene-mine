"""
AI Recipe Generator Service Implementation

This service uses LangChain with Mistral to generate recipes from user prompts.
For testing purposes, a mock generator is also provided.
"""

from typing import Any

from langchain.messages import AIMessage
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_mistralai import ChatMistralAI

from ..domain.ports.ai_recipe_generator import AIRecipeGeneratorPort
from ..settings import Settings, get_settings


class RecipeAIGenerator(AIRecipeGeneratorPort):
    """
    Production AI recipe generator service.

    Uses LangChain with Mistral to generate recipes.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        model: str | None = None,
        max_recipes: int | None = None,
    ):
        """
        Initialize the AI recipe generator.

        Args:
            settings: Application settings (uses global settings if None)
            model: Model to use for generation (overrides settings)
            max_recipes: Maximum number of recipes to generate (overrides settings)
        """
        self._settings = settings or get_settings()
        self._model = model or self._settings.ai_model
        self._max_recipes = max_recipes or self._settings.ai_max_drafts
        self._llm = ChatMistralAI(
            api_key=self._settings.mistral_api_key,
            model=self._model,
            temperature=0.7,
            max_tokens=2000,
        )

    async def generate_recipes(self, prompt: str, max_recipes: int | None = None) -> list[dict[str, Any]]:
        """
        Generate recipe drafts from a user prompt.

        Args:
            prompt: User instruction for recipe generation
            max_recipes: Maximum number of recipes to generate (overrides instance default)

        Returns:
            List of recipe dictionaries with title, content, summary, etc.
        """
        num_recipes = max_recipes if max_recipes is not None else self._max_recipes
        return await self._generate_with_ai(prompt, num_recipes)

    async def _generate_with_ai(self, prompt: str, num_recipes: int) -> list[dict[str, Any]]:
        """
        Generate recipes using actual AI (LangChain/LangGraph with Mistral).

        Uses LangChain's ChatMistralAI to generate recipe ideas from user prompts.
        Returns structured recipe data with title, content, summary, etc.
        """

        output_parser = StrOutputParser()
        system_prompt = self._get_system_prompt()
        human_prompt = f"Generate {num_recipes} recipe(s) based on: {prompt}"
        messages: list[BaseMessage] = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]

        response: AIMessage = await self._llm.ainvoke(messages)
        parsed_response = output_parser.parse(response.content)

        return self._parse_ai_response(parsed_response, num_recipes)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for recipe generation."""
        return """You are an expert chef and recipe creator.
Your task is to generate detailed, practical, and delicious recipes based on user requests.

For each recipe, provide:
1. A clear, descriptive title
2. A brief summary (1-2 sentences)
3. A list of ingredients with quantities
4. Step-by-step instructions
5. Estimated servings, prep time, and cook time
6. Difficulty level (Easy, Medium, Hard)

Format each recipe as a JSON object with the following structure:
{
    "title": "Recipe Title",
    "summary": "Brief description of the recipe",
    "content": "Full recipe in markdown format with headers, ingredients, and instructions",
    "ingredients": ["list", "of", "ingredients"],
    "instructions": ["step 1", "step 2", "..."],
    "servings": 4,
    "prep_time": "20 minutes",
    "cook_time": "30 minutes",
    "difficulty": "Medium"
}

Return ONLY a JSON array of recipe objects, no other text.

Remember:
- Be creative but practical
- Use realistic ingredient quantities
- Include clear, actionable instructions
- Consider dietary restrictions if mentioned in the prompt
- Always provide complete, usable recipes"""

    def _parse_ai_response(self, response: str, num_recipes: int) -> list[dict[str, Any]]:
        """
        Parse the AI response into structured recipe data.

        Handles both single recipe and multiple recipes responses.
        """
        import json

        # Clean up the response
        response = response.strip()

        # Try to parse as JSON array first
        try:
            recipes = json.loads(response)
            if isinstance(recipes, list):
                # Validate and normalize each recipe
                return [self._normalize_recipe(r) for r in recipes[:num_recipes]]
            elif isinstance(recipes, dict):
                # Single recipe, wrap in list
                return [self._normalize_recipe(recipes)]
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown or other formatting
        try:
            import re

            # Look for JSON array
            array_match = re.search(r"\[.*\]", response, re.DOTALL)
            if array_match:
                recipes = json.loads(array_match.group(0))
                return [self._normalize_recipe(r) for r in recipes[:num_recipes]]

            # Look for single JSON object
            json_match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
            if json_match:
                recipe = json.loads(json_match.group(0))
                return [self._normalize_recipe(recipe)]
        except (json.JSONDecodeError, AttributeError):
            pass

        # If all parsing fails, return empty list
        # The caller should handle this case appropriately
        return []

    def _normalize_recipe(self, recipe: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize a recipe dictionary to ensure all required fields are present.
        """
        # Ensure all required fields are present with defaults
        normalized = {
            "title": str(recipe.get("title", "Untitled Recipe")),
            "summary": str(recipe.get("summary", "A delicious recipe")),
            "content": str(
                recipe.get(
                    "content",
                    f"# {recipe.get('title', 'Untitled Recipe')}\n\n"
                    f"## Summary\n{recipe.get('summary', 'A delicious recipe')}\n\n"
                    f"## Ingredients\n"
                    f"\n".join(recipe.get("ingredients", [])),
                )
            ),
            "ingredients": recipe.get("ingredients", []),
            "instructions": recipe.get("instructions", []),
            "servings": int(recipe.get("servings", 4)),
            "prep_time": str(recipe.get("prep_time", "20 minutes")),
            "cook_time": str(recipe.get("cook_time", "30 minutes")),
            "difficulty": str(recipe.get("difficulty", "Medium")),
        }

        # Ensure ingredients and instructions are lists of strings
        if not isinstance(normalized["ingredients"], list):
            normalized["ingredients"] = [str(normalized["ingredients"])]
        if not isinstance(normalized["instructions"], list):
            normalized["instructions"] = [str(normalized["instructions"])]

        # Ensure all list items are strings
        normalized["ingredients"] = [str(ing) for ing in normalized["ingredients"]]
        normalized["instructions"] = [str(inst) for inst in normalized["instructions"]]

        return normalized
