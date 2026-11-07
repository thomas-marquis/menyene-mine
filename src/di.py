from typing import Annotated

from fastapi import Depends

from .infra.db import AsyncSession, get_session
from .infra.repositories.item_repository import ItemRepositoryImpl
from .use_cases.item_use_cases import ItemUseCases


def get_item_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> ItemRepositoryImpl:
    """Dependency for ItemRepository."""
    return ItemRepositoryImpl(session)


def get_item_use_cases(
    repository: Annotated[ItemRepositoryImpl, Depends(get_item_repository)],
) -> ItemUseCases:
    """Dependency for ItemUseCases."""
    return ItemUseCases(repository)
