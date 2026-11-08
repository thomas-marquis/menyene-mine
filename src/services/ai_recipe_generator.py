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


class MockRecipeAIGenerator(AIRecipeGeneratorPort):
    """
    Mock implementation of AI recipe generator for testing.

    Always uses mock generation regardless of settings.
    """

    def __init__(self, max_recipes: int = 10):
        """
        Initialize the mock AI recipe generator.

        Args:
            max_recipes: Maximum number of recipes to generate
        """
        import random

        self.max_recipes = max_recipes
        self._random = random

    async def generate_recipes(self, prompt: str, max_recipes: int | None = None) -> list[dict[str, Any]]:
        """
        Generate mock recipe drafts from a user prompt.

        Args:
            prompt: User instruction for recipe generation
            max_recipes: Maximum number of recipes to generate

        Returns:
            List of mock recipe dictionaries
        """
        num_recipes = max_recipes if max_recipes is not None else self.max_recipes
        return await self._generate_mock_recipes(prompt, num_recipes)

    async def _generate_mock_recipes(self, prompt: str, num_recipes: int) -> list[dict[str, Any]]:
        """Generate mock recipes for testing without API key."""
        # Extract keywords from prompt for more relevant mocks
        keywords = [word.lower() for word in prompt.split() if len(word) > 3]

        recipes = []
        for i in range(min(num_recipes, self.max_recipes)):
            recipe = self._create_mock_recipe(prompt, keywords, i + 1)
            recipes.append(recipe)

        return recipes

    def _create_mock_recipe(self, prompt: str, keywords: list[str], index: int) -> dict[str, Any]:
        """Create a single mock recipe."""
        # Select a main keyword for the recipe
        main_keyword = keywords[0] if keywords else "delicious"

        # Generate a title
        adjectives = [
            "Delicious",
            "Easy",
            "Quick",
            "Healthy",
            "Gourmet",
            "Traditional",
            "Spicy",
        ]
        nouns = ["Recipe", "Dish", "Meal", "Creation", "Delight", "Specialty"]
        title = f"{self._random.choice(adjectives)} {main_keyword.capitalize()} {self._random.choice(nouns)}"

        # Generate ingredients
        ingredients = self._generate_mock_ingredients(main_keyword)

        # Generate instructions
        instructions = self._generate_mock_instructions(main_keyword)

        # Generate summary
        adjective = self._random.choice(adjectives).lower()
        summary = (
            f"A {adjective} {main_keyword} recipe that's perfect for any occasion. "
            f"This dish serves {self._random.randint(2, 6)} and takes about "
            f"{self._random.randint(20, 90)} minutes to prepare."
        )

        # Generate content (full recipe in markdown format)
        content = (
            f"# {title}\n\n"
            f"## Summary\n"
            f"{summary}\n\n"
            f"## Ingredients\n"
            f"{ingredients}\n\n"
            f"## Instructions\n"
            f"{instructions}\n\n"
            f"## Tips\n"
            f"- Make sure all ingredients are fresh\n"
            f"- Adjust seasoning to taste\n"
            f"- Serve warm for best results"
        )

        return {
            "title": title,
            "content": content,
            "summary": summary,
            "ingredients": ingredients.split("\n"),
            "instructions": instructions.split("\n"),
            "servings": self._random.randint(2, 6),
            "prep_time": f"{self._random.randint(10, 45)} minutes",
            "cook_time": f"{self._random.randint(15, 60)} minutes",
            "difficulty": self._random.choice(["Easy", "Medium", "Hard"]),
        }

    def _generate_mock_ingredients(self, keyword: str) -> str:
        """Generate mock ingredients list."""
        base_ingredients = [
            "Salt and pepper to taste",
            "2 tablespoons olive oil",
            "1 onion, finely chopped",
            "2 cloves garlic, minced",
        ]

        keyword_ingredients = {
            "chicken": [
                "500g chicken breast",
                "1 teaspoon paprika",
                "1/2 cup chicken broth",
            ],
            "pasta": ["250g pasta", "1 cup tomato sauce", "1/2 cup grated parmesan"],
            "salad": [
                "1 head lettuce",
                "2 tomatoes",
                "1 cucumber",
                "1/4 cup olive oil",
            ],
            "soup": [
                "1 liter vegetable broth",
                "2 carrots",
                "2 celery stalks",
                "1 bay leaf",
            ],
            "cake": [
                "200g flour",
                "150g sugar",
                "3 eggs",
                "100g butter",
                "1 teaspoon baking powder",
            ],
            "pizza": [
                "1 pizza dough",
                "1/2 cup tomato sauce",
                "200g mozzarella",
                "Toppings of choice",
            ],
        }

        # Get keyword-specific ingredients or use generic ones
        specific = keyword_ingredients.get(keyword.lower(), [])
        all_ingredients = base_ingredients + specific

        # Randomly select 5-8 ingredients
        selected = self._random.sample(all_ingredients, min(5, len(all_ingredients)))
        if len(specific) > 0 and specific[0] not in selected:
            selected.insert(0, specific[0])

        return "\n".join([f"- {ing}" for ing in selected[:8]])

    def _generate_mock_instructions(self, keyword: str) -> str:
        """Generate mock instructions."""
        base_instructions = [
            "Preheat your oven to 180°C (350°F).",
            "Heat oil in a large pan over medium heat.",
            "Add onions and garlic, sauté until fragrant.",
            "Season with salt and pepper to taste.",
            "Simmer for 15-20 minutes until cooked through.",
            "Let it rest for 5 minutes before serving.",
        ]

        keyword_instructions = {
            "chicken": [
                "Season chicken breast with salt, pepper, and paprika.",
                "Cook chicken for 6-8 minutes on each side until golden brown.",
                "Add chicken broth and bring to a simmer.",
            ],
            "pasta": [
                "Cook pasta according to package instructions until al dente.",
                "Drain pasta, reserving 1/2 cup of pasta water.",
                "Toss pasta with tomato sauce and parmesan cheese.",
            ],
            "cake": [
                "Cream together butter and sugar until light and fluffy.",
                "Add eggs one at a time, beating well after each addition.",
                "Fold in dry ingredients alternately with wet ingredients.",
                "Bake for 25-30 minutes or until a toothpick comes out clean.",
            ],
        }

        specific = keyword_instructions.get(keyword.lower(), [])
        all_instructions = base_instructions + specific

        # Select and order instructions
        selected = self._random.sample(all_instructions, min(6, len(all_instructions)))
        if specific:
            # Ensure keyword-specific instructions come first
            selected = specific + [i for i in selected if i not in specific]

        return "\n".join([f"{i + 1}. {inst}" for i, inst in enumerate(selected[:8])])
