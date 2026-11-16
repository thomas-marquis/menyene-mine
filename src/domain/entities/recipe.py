from dataclasses import dataclass
from datetime import datetime


@dataclass
class Recipe:
    """
    Recipe domain entity.

    Represents a complete recipe with all required fields.
    This is a pure domain object with no external dependencies.
    """

    id: int | None = None
    title: str | None = None
    creation_date: datetime | None = None
    last_updated: datetime | None = None
    summary: str | None = None
    ingredients: list[str] | None = None
    instructions: list[str] | None = None
    servings: int | None = None
    prep_time: str | None = None
    cook_time: str | None = None
    difficulty: str | None = None

    def to_markdown(self) -> str:
        """
        Convert recipe to markdown format.

        Returns:
            Recipe formatted as markdown string
        """
        ingredients_md = "\n".join(f"- {ingredient}" for ingredient in (self.ingredients or []))
        instructions_md = "\n".join(f"{i + 1}. {instruction}" for i, instruction in enumerate(self.instructions or []))

        return f"""# {self.title or "Untitled Recipe"}

## Summary
{self.summary or ""}

## Ingredients
{ingredients_md}

## Instructions
{instructions_md}

## Details
- **Servings:** {self.servings or 4}
- **Prep Time:** {self.prep_time or "0 minutes"}
- **Cook Time:** {self.cook_time or "0 minutes"}
- **Difficulty:** {self.difficulty or "Medium"}
"""
