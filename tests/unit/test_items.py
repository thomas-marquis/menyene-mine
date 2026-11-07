from unittest.mock import AsyncMock

import pytest

from src.domain.entities.item import Item
from src.infra.repositories.item_repository import ItemRepositoryImpl
from src.use_cases.item_use_cases import ItemUseCases


class TestItemUseCases:
    @pytest.mark.asyncio
    async def test_should_create_item_when_name_provided(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=ItemRepositoryImpl)
        mock_item = Item(id="test-id", name="Test Item", created_at=None)
        mock_repo.create.return_value = mock_item
        use_cases = ItemUseCases(mock_repo)

        # When
        result = await use_cases.create_item("Test Item")

        # Then
        assert result.name == "Test Item"
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_no_items_exist(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=ItemRepositoryImpl)
        mock_repo.list_all.return_value = []
        use_cases = ItemUseCases(mock_repo)

        # When
        result = await use_cases.list_items()

        # Then
        assert result == []
        mock_repo.list_all.assert_called_once()
