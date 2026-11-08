"""
API routes for recipe drafts.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...di import get_recipe_draft_use_cases, get_recipe_use_cases
from ...domain.entities.recipe_draft import RecipeDraftStatus
from ...use_cases.recipe_draft_use_cases import RecipeDraftUseCases
from ...use_cases.recipe_use_cases import RecipeUseCases
from .schemas import (
    RecipeDraftActionResponse,
    RecipeDraftGenerateRequest,
    RecipeDraftListResponse,
    RecipeDraftResponse,
    RecipeDraftStatsResponse,
    RecipeResponse,
)

router = APIRouter(prefix="/recipe-drafts", tags=["recipe-drafts"])

RecipeDraftUseCasesDep = Annotated[RecipeDraftUseCases, Depends(get_recipe_draft_use_cases)]
RecipeUseCasesDep = Annotated[RecipeUseCases, Depends(get_recipe_use_cases)]


def _draft_entity_to_response(draft: Any) -> RecipeDraftResponse:
    """Convert domain RecipeDraft entity to RecipeDraftResponse schema."""
    from ...domain.entities.recipe_draft import RecipeDraft

    if isinstance(draft, RecipeDraft):
        return RecipeDraftResponse(
            id=draft.id,
            user_prompt=draft.user_prompt or "",
            generated_content=draft.generated_content or {},
            status=draft.status.value if draft.status else "draft",
            created_at=draft.created_at,
            updated_at=draft.updated_at,
            recipe_id=draft.recipe_id,
        )
    # This should not happen in normal operation, but we need to satisfy mypy
    raise ValueError(f"Expected RecipeDraft, got {type(draft)}")


@router.post(
    "/generate",
    response_model=list[RecipeDraftResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate recipe drafts from a prompt",
    description="Uses AI to generate recipe drafts based on user instructions",
)
async def generate_drafts_endpoint(
    request: RecipeDraftGenerateRequest,
    use_cases: RecipeDraftUseCasesDep,
) -> list[RecipeDraftResponse]:
    """Generate recipe drafts from a user prompt."""
    try:
        drafts = await use_cases.generate_drafts(
            user_prompt=request.prompt,
            max_drafts=request.max_drafts,
        )
        return [_draft_entity_to_response(d) for d in drafts]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate drafts: {str(e)}",
        ) from e


@router.get(
    "/",
    response_model=RecipeDraftListResponse,
    summary="List all recipe drafts",
    description="List all recipe drafts with optional status filtering",
)
async def list_drafts_endpoint(
    use_cases: RecipeDraftUseCasesDep,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    status_filter: str | None = Query(
        None, description="Filter by status: draft, validated, rejected"
    ),
) -> RecipeDraftListResponse:
    """List all recipe drafts with optional filtering."""
    try:
        # Convert status string to enum if provided
        status_enum = None
        if status_filter:
            try:
                status_enum = RecipeDraftStatus(status_filter)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Invalid status: {status_filter}. "
                        "Must be one of: draft, validated, rejected"
                    ),
                ) from e

        drafts = await use_cases.list_drafts(skip=skip, limit=limit, status=status_enum)
        total = await use_cases.count_drafts(status=status_enum)

        return RecipeDraftListResponse(
            drafts=[_draft_entity_to_response(d) for d in drafts],
            total=total,
            skip=skip,
            limit=limit,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list drafts: {str(e)}",
        ) from e


@router.get(
    "/stats",
    response_model=RecipeDraftStatsResponse,
    summary="Get recipe draft statistics",
    description="Get counts of drafts by status",
)
async def get_draft_stats_endpoint(
    use_cases: RecipeDraftUseCasesDep,
) -> RecipeDraftStatsResponse:
    """Get statistics about recipe drafts."""
    try:
        stats = await use_cases.get_draft_stats()
        return RecipeDraftStatsResponse(
            total=stats["total"],
            draft=stats["draft"],
            validated=stats["validated"],
            rejected=stats["rejected"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get draft stats: {str(e)}",
        ) from e


@router.get(
    "/{draft_id}",
    response_model=RecipeDraftResponse,
    summary="Get a specific recipe draft",
    description="Get details of a specific recipe draft by ID",
)
async def get_draft_endpoint(
    draft_id: int,
    use_cases: RecipeDraftUseCasesDep,
) -> RecipeDraftResponse:
    """Get a specific recipe draft by ID."""
    draft = await use_cases.get_draft(draft_id)
    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe draft with id {draft_id} not found",
        )
    return _draft_entity_to_response(draft)


@router.post(
    "/{draft_id}/validate",
    response_model=RecipeDraftActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate a recipe draft",
    description="Validate a draft and create an actual recipe from it",
)
async def validate_draft_endpoint(
    draft_id: int,
    use_cases: RecipeDraftUseCasesDep,
) -> RecipeDraftActionResponse:
    """Validate a draft and create a recipe from it."""
    try:
        # Get the draft first to return in response
        draft = await use_cases.get_draft(draft_id)
        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe draft with id {draft_id} not found",
            )

        # Validate the draft (creates recipe)
        recipe = await use_cases.validate_draft(draft_id)

        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create recipe from draft",
            )

        # Get updated draft
        updated_draft = await use_cases.get_draft(draft_id)

        return RecipeDraftActionResponse(
            success=True,
            message="Draft validated and recipe created successfully",
            draft=_draft_entity_to_response(updated_draft) if updated_draft else None,
            recipe=RecipeResponse(
                id=recipe.id,
                title=recipe.title,
                creation_date=recipe.creation_date,
                last_updated=recipe.last_updated,
                content=recipe.content,
                summary=recipe.summary,
            )
            if recipe
            else None,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate draft: {str(e)}",
        ) from e


@router.post(
    "/{draft_id}/reject",
    response_model=RecipeDraftActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject a recipe draft",
    description="Mark a draft as rejected",
)
async def reject_draft_endpoint(
    draft_id: int,
    use_cases: RecipeDraftUseCasesDep,
) -> RecipeDraftActionResponse:
    """Reject a recipe draft."""
    try:
        draft = await use_cases.get_draft(draft_id)
        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe draft with id {draft_id} not found",
            )

        rejected_draft = await use_cases.reject_draft(draft_id)

        if rejected_draft is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reject draft",
            )

        return RecipeDraftActionResponse(
            success=True,
            message="Draft rejected successfully",
            draft=_draft_entity_to_response(rejected_draft),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject draft: {str(e)}",
        ) from e


@router.delete(
    "/{draft_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recipe draft",
    description="Delete a recipe draft by ID",
)
async def delete_draft_endpoint(
    draft_id: int,
    use_cases: RecipeDraftUseCasesDep,
) -> None:
    """Delete a recipe draft."""
    success = await use_cases.delete_draft(draft_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe draft with id {draft_id} not found",
        )
