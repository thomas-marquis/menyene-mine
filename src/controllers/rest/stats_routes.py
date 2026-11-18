"""Routes for resource statistics."""

from typing import Annotated

from fastapi import APIRouter, Depends

from ...di import get_stats_use_cases
from ...use_cases.stats_use_cases import StatsUseCases
from .schemas import StatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])

StatsUseCasesDep = Annotated[StatsUseCases, Depends(get_stats_use_cases)]


@router.get("/", response_model=StatsResponse)
async def get_stats_endpoint(use_cases: StatsUseCasesDep) -> StatsResponse:
    """Get statistics for all resources.

    Returns:
        StatsResponse: Object containing statistics for recipes, drafts, and groceries
    """
    stats = await use_cases.get_all_stats()
    return StatsResponse.model_validate(stats)
