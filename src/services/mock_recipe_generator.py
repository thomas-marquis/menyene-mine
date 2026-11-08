from typing import Any

from ..domain.ports.ai_recipe_generator import AIRecipeGeneratorPort


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
