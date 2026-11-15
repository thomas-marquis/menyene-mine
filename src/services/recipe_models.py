"""
Pydantic models for recipe data structures.

These models define the structure and validation rules for recipe data
used in AI generation and validation.
"""

from pydantic import BaseModel, Field


class GeneratedRecipe(BaseModel):
    """
    Pydantic model for a single generated recipe with Field annotations.

    This model defines the structure for recipe generation output with
    proper validation, descriptions for the LLM, and default values.
    """

    title: str = Field(
        ...,
        description="The title of the recipe, should be descriptive and catchy",
        min_length=3,
        max_length=300,
    )

    summary: str = Field(
        ...,
        description="A brief summary of the recipe, highlighting its main features",
        min_length=10,
        max_length=500,
    )

    ingredients: list[str] = Field(
        ...,
        description="List of ingredients needed for the recipe",
        min_length=1,
        max_length=100,
    )

    instructions: list[str] = Field(
        ...,
        description="Step-by-step instructions for preparing the recipe",
        min_length=1,
        max_length=100,
    )

    servings: int = Field(
        default=4,
        ge=1,
        description="Number of servings the recipe produces",
    )

    prep_time: str = Field(
        default="20 minutes",
        description="Preparation time required for the recipe",
    )

    cook_time: str = Field(
        default="30 minutes",
        description="Cooking time required for the recipe",
    )

    difficulty: str = Field(
        default="Medium",
        description="Difficulty level of the recipe: Easy, Medium, or Hard",
    )
