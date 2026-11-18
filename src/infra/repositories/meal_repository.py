from datetime import UTC, date

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.meal import Meal, MealMoment
from ...domain.ports.meal_repository import MealRepositoryPort
from ..models.meal import Meal as MealModel


class MealRepositoryImpl(MealRepositoryPort):
    """
    SQLAlchemy implementation of MealRepositoryPort.

    Provides database operations for Meal entities.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, meal: Meal) -> Meal:
        """Create a new meal plan entry."""
        meal_model = MealModel(
            date=meal.date,
            moment=meal.moment.value if isinstance(meal.moment, MealMoment) else meal.moment,
            recipe_id=meal.recipe_id,
        )
        self._session.add(meal_model)
        await self._session.commit()
        await self._session.refresh(meal_model)

        return Meal(
            id=meal_model.id,
            date=meal_model.date,
            moment=MealMoment(meal_model.moment),
            recipe_id=meal_model.recipe_id,
            created_at=meal_model.created_at,
            updated_at=meal_model.updated_at,
        )

    async def get_by_id(self, meal_id: int) -> Meal | None:
        """Get a meal by its ID."""
        result = await self._session.execute(select(MealModel).where(MealModel.id == meal_id))
        meal_model = result.scalar_one_or_none()

        if meal_model is None:
            return None

        return Meal(
            id=meal_model.id,
            date=meal_model.date,
            moment=MealMoment(meal_model.moment),
            recipe_id=meal_model.recipe_id,
            created_at=meal_model.created_at,
            updated_at=meal_model.updated_at,
        )

    async def get_by_date_and_moment(self, date: date, moment: MealMoment) -> Meal | None:
        """Get a meal by its date and moment."""
        moment_str = moment.value if isinstance(moment, MealMoment) else moment
        result = await self._session.execute(
            select(MealModel).where(
                and_(
                    MealModel.date == date,
                    MealModel.moment == moment_str,
                )
            )
        )
        meal_model = result.scalar_one_or_none()

        if meal_model is None:
            return None

        return Meal(
            id=meal_model.id,
            date=meal_model.date,
            moment=MealMoment(meal_model.moment),
            recipe_id=meal_model.recipe_id,
            created_at=meal_model.created_at,
            updated_at=meal_model.updated_at,
        )

    async def get_meals_for_month(self, year: int, month: int) -> list[Meal]:
        """Get all meals for a specific month."""
        start_date = date(year, month, 1)
        end_date = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)

        result = await self._session.execute(
            select(MealModel).where(
                and_(
                    MealModel.date >= start_date,
                    MealModel.date < end_date,
                )
            )
        )
        meal_models = result.scalars().all()

        return [
            Meal(
                id=meal_model.id,
                date=meal_model.date,
                moment=MealMoment(meal_model.moment),
                recipe_id=meal_model.recipe_id,
                created_at=meal_model.created_at,
                updated_at=meal_model.updated_at,
            )
            for meal_model in meal_models
        ]

    async def update(self, meal: Meal) -> Meal | None:
        """Update an existing meal."""
        result = await self._session.execute(select(MealModel).where(MealModel.id == meal.id))
        meal_model = result.scalar_one_or_none()

        if meal_model is None:
            return None

        if meal.recipe_id is not None:
            meal_model.recipe_id = meal.recipe_id
        meal_model.updated_at = func.now(UTC)
        await self._session.commit()
        await self._session.refresh(meal_model)

        return Meal(
            id=meal_model.id,
            date=meal_model.date,
            moment=MealMoment(meal_model.moment),
            recipe_id=meal_model.recipe_id,
            created_at=meal_model.created_at,
            updated_at=meal_model.updated_at,
        )

    async def delete(self, meal_id: int) -> bool:
        """Delete a meal by its ID."""
        result = await self._session.execute(delete(MealModel).where(MealModel.id == meal_id))
        await self._session.commit()
        # rowcount is available on the result object
        return bool(result.rowcount > 0)  # type: ignore[attr-defined]

    async def get_meals_by_recipe_id(self, recipe_id: int) -> list[Meal]:
        """Get all meals that reference a specific recipe."""
        result = await self._session.execute(select(MealModel).where(MealModel.recipe_id == recipe_id))
        meal_models = result.scalars().all()

        return [
            Meal(
                id=meal_model.id,
                date=meal_model.date,
                moment=MealMoment(meal_model.moment),
                recipe_id=meal_model.recipe_id,
                created_at=meal_model.created_at,
                updated_at=meal_model.updated_at,
            )
            for meal_model in meal_models
        ]
