from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.recipe import Recipe as RecipeEntity
from ...domain.ports.recipe_repository import RecipeRepositoryPort
from ..models.recipe import Recipe as RecipeModel


class RecipeRepositoryImpl(RecipeRepositoryPort):
    """SQLAlchemy implementation of Recipe repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, recipe: RecipeEntity) -> RecipeEntity:
        """Create a new recipe in the database."""
        recipe_model = RecipeModel(
            title=recipe.title,
            content=recipe.content,
            summary=recipe.summary,
        )
        self.session.add(recipe_model)
        await self.session.commit()
        await self.session.refresh(recipe_model)
        return RecipeEntity(
            id=recipe_model.id,
            title=recipe_model.title,
            creation_date=recipe_model.creation_date,
            last_updated=recipe_model.last_updated,
            content=recipe_model.content,
            summary=recipe_model.summary,
        )

    async def get_by_id(self, recipe_id: int) -> RecipeEntity | None:
        """Get a recipe by its ID."""
        result = await self.session.execute(select(RecipeModel).where(RecipeModel.id == recipe_id))
        recipe_model = result.scalar_one_or_none()
        if recipe_model is None:
            return None
        return RecipeEntity(
            id=recipe_model.id,
            title=recipe_model.title,
            creation_date=recipe_model.creation_date,
            last_updated=recipe_model.last_updated,
            content=recipe_model.content,
            summary=recipe_model.summary,
        )

    async def update(self, recipe: RecipeEntity) -> RecipeEntity | None:
        """Update an existing recipe."""
        result = await self.session.execute(select(RecipeModel).where(RecipeModel.id == recipe.id))
        recipe_model = result.scalar_one_or_none()
        if recipe_model is None:
            return None

        if recipe.title is not None:
            recipe_model.title = recipe.title
        if recipe.content is not None:
            recipe_model.content = recipe.content
        if recipe.summary is not None:
            recipe_model.summary = recipe.summary
        await self.session.commit()
        await self.session.refresh(recipe_model)
        return RecipeEntity(
            id=recipe_model.id,
            title=recipe_model.title,
            creation_date=recipe_model.creation_date,
            last_updated=recipe_model.last_updated,
            content=recipe_model.content,
            summary=recipe_model.summary,
        )

    async def delete(self, recipe_id: int) -> bool:
        """Delete a recipe by its ID."""
        result = await self.session.execute(select(RecipeModel).where(RecipeModel.id == recipe_id))
        recipe_model = result.scalar_one_or_none()
        if recipe_model is None:
            return False

        await self.session.delete(recipe_model)
        await self.session.commit()
        return True

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[RecipeEntity]:
        """List all recipes with pagination."""
        result = await self.session.execute(
            select(RecipeModel).order_by(RecipeModel.creation_date.desc()).offset(skip).limit(limit)
        )
        recipes = result.scalars().all()
        return [
            RecipeEntity(
                id=r.id,
                title=r.title,
                creation_date=r.creation_date,
                last_updated=r.last_updated,
                content=r.content,
                summary=r.summary,
            )
            for r in recipes
        ]

    async def search(self, keyword: str, skip: int = 0, limit: int = 100) -> list[RecipeEntity]:
        """Search recipes by keyword in title or content."""
        result = await self.session.execute(
            select(RecipeModel)
            .where(
                or_(
                    RecipeModel.title.ilike(f"%{keyword}%"),
                    RecipeModel.content.ilike(f"%{keyword}%"),
                )
            )
            .order_by(RecipeModel.creation_date.desc())
            .offset(skip)
            .limit(limit)
        )
        recipes = result.scalars().all()
        return [
            RecipeEntity(
                id=r.id,
                title=r.title,
                creation_date=r.creation_date,
                last_updated=r.last_updated,
                content=r.content,
                summary=r.summary,
            )
            for r in recipes
        ]
