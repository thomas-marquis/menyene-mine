"""
Mock Recipe Generator for testing.

This implementation provides mock recipe generation without requiring
an AI API key. It's used when AI is disabled in the configuration.
"""

import random

from ..domain.entities.recipe import Recipe as RecipeEntity
from .recipe_generator import RecipeGenerator


class MockRecipeAIGenerator(RecipeGenerator):
    """
    Mock implementation of recipe generator for testing.

    Always uses mock generation regardless of settings.
    """

    def __init__(self) -> None:
        """Initialize the mock recipe generator."""
        self._random = random

    async def generate_recipe(self, instruction: str) -> RecipeEntity:
        """
        Generate a single mock recipe draft from a user instruction.

        Args:
            instruction: User instruction for recipe generation

        Returns:
            Mock Recipe domain entity
        """
        return self._create_mock_recipe(instruction, 1)

    def _create_mock_recipe(self, instruction: str, index: int) -> RecipeEntity:
        """Create a single mock recipe as a domain entity."""
        # Extract keywords from instruction for more relevant mocks
        keywords = [word.lower() for word in instruction.split() if len(word) > 3]
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
        ingredients_str = self._generate_mock_ingredients(main_keyword)
        ingredients = [ing.strip("- ") for ing in ingredients_str.split("\n") if ing.strip()]

        # Generate instructions
        instructions_str = self._generate_mock_instructions(main_keyword)
        raw_instructions = instructions_str.split("\n")
        instructions = []
        for inst in raw_instructions:
            if inst.strip():
                if ". " in inst:
                    instructions.append(inst.split(". ", 1)[1].strip())
                else:
                    instructions.append(inst.strip())

        # Generate summary
        adjective = self._random.choice(adjectives).lower()
        servings = self._random.randint(2, 6)
        prep_time_minutes = self._random.randint(20, 90)
        summary = (
            f"A {adjective} {main_keyword} recipe that's perfect for any occasion. "
            f"This dish serves {servings} and takes about {prep_time_minutes} minutes to prepare."
        )

        return RecipeEntity(
            title=title,
            summary=summary,
            ingredients=ingredients,
            instructions=instructions,
            servings=servings,
            prep_time=f"{prep_time_minutes} minutes",
            cook_time="30 minutes",
            difficulty="Medium",
        )

    def _format_recipe_content(self, title: str, summary: str, ingredients: str, instructions: str) -> str:
        """Format recipe content in markdown format."""
        return (
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
