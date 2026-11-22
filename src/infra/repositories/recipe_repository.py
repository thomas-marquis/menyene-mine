from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.recipe import Recipe as RecipeEntity
from ...domain.entities.search_result import SearchResult
from ...domain.ports.recipe_repository import RecipeRepositoryPort
from ..models.recipe import Recipe as RecipeModel


class RecipeRepositoryImpl(RecipeRepositoryPort):
    """SQLAlchemy implementation of Recipe repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, recipe: RecipeEntity) -> RecipeEntity:
        """Create a new recipe in the database."""
        recipe_model = RecipeModel(
            title=recipe.title,
            summary=recipe.summary,
            ingredients=recipe.ingredients or [],
            instructions=recipe.instructions or [],
            servings=recipe.servings or 4,
            prep_time=recipe.prep_time or "0 minutes",
            cook_time=recipe.cook_time or "0 minutes",
            difficulty=recipe.difficulty or "Medium",
        )
        self._session.add(recipe_model)
        await self._session.commit()
        await self._session.refresh(recipe_model)
        return RecipeEntity(
            id=recipe_model.id,
            title=recipe_model.title,
            creation_date=recipe_model.creation_date,
            last_updated=recipe_model.last_updated,
            summary=recipe_model.summary,
            ingredients=recipe_model.ingredients,
            instructions=recipe_model.instructions,
            servings=recipe_model.servings,
            prep_time=recipe_model.prep_time,
            cook_time=recipe_model.cook_time,
            difficulty=recipe_model.difficulty,
        )

    async def get_by_id(self, recipe_id: int) -> RecipeEntity | None:
        """Get a recipe by its ID."""
        result = await self._session.execute(select(RecipeModel).where(RecipeModel.id == recipe_id))
        recipe_model = result.scalar_one_or_none()
        if recipe_model is None:
            return None
        return RecipeEntity(
            id=recipe_model.id,
            title=recipe_model.title,
            creation_date=recipe_model.creation_date,
            last_updated=recipe_model.last_updated,
            summary=recipe_model.summary,
            ingredients=recipe_model.ingredients,
            instructions=recipe_model.instructions,
            servings=recipe_model.servings,
            prep_time=recipe_model.prep_time,
            cook_time=recipe_model.cook_time,
            difficulty=recipe_model.difficulty,
        )

    async def update(self, recipe: RecipeEntity) -> RecipeEntity | None:
        """Update an existing recipe."""
        result = await self._session.execute(select(RecipeModel).where(RecipeModel.id == recipe.id))
        recipe_model = result.scalar_one_or_none()
        if recipe_model is None:
            return None

        if recipe.title is not None:
            recipe_model.title = recipe.title
        if recipe.summary is not None:
            recipe_model.summary = recipe.summary
        if recipe.ingredients is not None:
            recipe_model.ingredients = recipe.ingredients
        if recipe.instructions is not None:
            recipe_model.instructions = recipe.instructions
        if recipe.servings is not None:
            recipe_model.servings = recipe.servings
        if recipe.prep_time is not None:
            recipe_model.prep_time = recipe.prep_time
        if recipe.cook_time is not None:
            recipe_model.cook_time = recipe.cook_time
        if recipe.difficulty is not None:
            recipe_model.difficulty = recipe.difficulty
        await self._session.commit()
        await self._session.refresh(recipe_model)
        return RecipeEntity(
            id=recipe_model.id,
            title=recipe_model.title,
            creation_date=recipe_model.creation_date,
            last_updated=recipe_model.last_updated,
            summary=recipe_model.summary,
            ingredients=recipe_model.ingredients,
            instructions=recipe_model.instructions,
            servings=recipe_model.servings,
            prep_time=recipe_model.prep_time,
            cook_time=recipe_model.cook_time,
            difficulty=recipe_model.difficulty,
        )

    async def delete(self, recipe_id: int) -> bool:
        """Delete a recipe by its ID."""
        result = await self._session.execute(select(RecipeModel).where(RecipeModel.id == recipe_id))
        recipe_model = result.scalar_one_or_none()
        if recipe_model is None:
            return False

        await self._session.delete(recipe_model)
        await self._session.commit()
        return True

    async def list_all(self, skip: int = 0, limit: int = 100) -> SearchResult:
        """List all recipes with pagination."""
        # Get the recipes for the current page
        result = await self._session.execute(
            select(RecipeModel).order_by(RecipeModel.creation_date.desc()).offset(skip).limit(limit)
        )
        recipes = result.scalars().all()

        # Get the total count
        count_result = await self._session.execute(select(func.count()).select_from(RecipeModel))
        total = count_result.scalar() or 0

        return SearchResult(
            recipes=[
                RecipeEntity(
                    id=r.id,
                    title=r.title,
                    creation_date=r.creation_date,
                    last_updated=r.last_updated,
                    summary=r.summary,
                    ingredients=r.ingredients,
                    instructions=r.instructions,
                    servings=r.servings,
                    prep_time=r.prep_time,
                    cook_time=r.cook_time,
                    difficulty=r.difficulty,
                )
                for r in recipes
            ],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def search(self, keyword: str, skip: int = 0, limit: int = 100) -> SearchResult:
        """Search recipes by keyword in title, summary, ingredients, or instructions."""
        # Get the recipes for the current page
        result = await self._session.execute(
            select(RecipeModel)
            .where(
                or_(
                    RecipeModel.title.ilike(f"%{keyword}%"),
                    RecipeModel.summary.ilike(f"%{keyword}%"),
                )
            )
            .order_by(RecipeModel.creation_date.desc())
            .offset(skip)
            .limit(limit)
        )
        recipes = result.scalars().all()

        # Get the total count for this search
        count_result = await self._session.execute(
            select(func.count())
            .select_from(RecipeModel)
            .where(
                or_(
                    RecipeModel.title.ilike(f"%{keyword}%"),
                    RecipeModel.summary.ilike(f"%{keyword}%"),
                )
            )
        )
        total = count_result.scalar() or 0

        return SearchResult(
            recipes=[
                RecipeEntity(
                    id=r.id,
                    title=r.title,
                    creation_date=r.creation_date,
                    last_updated=r.last_updated,
                    summary=r.summary,
                    ingredients=r.ingredients,
                    instructions=r.instructions,
                    servings=r.servings,
                    prep_time=r.prep_time,
                    cook_time=r.cook_time,
                    difficulty=r.difficulty,
                )
                for r in recipes
            ],
            total=total,
            query=keyword,
            skip=skip,
            limit=limit,
        )

    async def update_instructions(self, recipe_id: int, instructions: list[str]) -> RecipeEntity | None:
        """Update only the instructions for a recipe."""
        result = await self._session.execute(select(RecipeModel).where(RecipeModel.id == recipe_id))
        recipe_model = result.scalar_one_or_none()
        if recipe_model is None:
            return None

        recipe_model.instructions = instructions
        await self._session.commit()
        await self._session.refresh(recipe_model)
        return RecipeEntity(
            id=recipe_model.id,
            title=recipe_model.title,
            creation_date=recipe_model.creation_date,
            last_updated=recipe_model.last_updated,
            summary=recipe_model.summary,
            ingredients=recipe_model.ingredients,
            instructions=recipe_model.instructions,
            servings=recipe_model.servings,
            prep_time=recipe_model.prep_time,
            cook_time=recipe_model.cook_time,
            difficulty=recipe_model.difficulty,
        )
