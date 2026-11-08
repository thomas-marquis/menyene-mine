# Data Model for recipe management

## Table: recipes

**Columns and types:**

- id: int, PK
- title: varchar, the recipe short title (e.g., "Spaghetti Bolognese")
- creation_date: datetime, the date when the recipe was created
- last_updated: datetime, the date when the recipe was last updated
- content: text, the full content of the recipe (ingredients, steps, etc.), in markdown format
- summary: text, a short summary of the recipe (< 500 characters)