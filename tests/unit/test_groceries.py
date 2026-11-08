from unittest.mock import AsyncMock

import pytest

from src.controllers.rest.schemas import GroceryItemCreate, GroceryItemUpdate
from src.domain.entities.grocery_item import GroceryItem
from src.infra.repositories.grocery_repository import GroceryRepositoryImpl
from src.use_cases.grocery_use_cases import GroceryUseCases


class TestGrocerySchemas:
    def test_should_reject_empty_name_in_create_schema(self) -> None:
        # Given/When/Then - Pydantic should reject empty name
        from pydantic import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            GroceryItemCreate(name="", quantity="2 units")
        assert "min_length" in str(exc_info.value) or "at least 1 character" in str(exc_info.value)

    def test_should_reject_empty_name_in_update_schema(self) -> None:
        # Given/When/Then - Pydantic should reject empty name
        from pydantic import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            GroceryItemUpdate(name="", quantity="2 units")
        assert "min_length" in str(exc_info.value) or "at least 1 character" in str(exc_info.value)


class TestGroceryUseCases:
    @pytest.mark.asyncio
    async def test_should_create_grocery_item_when_valid_data_provided(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        mock_grocery_item = GroceryItem(
            id=1,
            name="Test Grocery Item",
            quantity="2 units",
            is_completed=False,
            created_at=None,
            updated_at=None,
        )
        mock_repo.create.return_value = mock_grocery_item
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.create_grocery_item(
            name="Test Grocery Item",
            quantity="2 units",
            is_completed=False,
        )

        # Then
        assert result.name == "Test Grocery Item"
        assert result.quantity == "2 units"
        assert result.is_completed is False
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_create_grocery_item_with_default_values(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        mock_grocery_item = GroceryItem(
            id=1,
            name="Test Grocery Item",
            quantity=None,
            is_completed=False,
            created_at=None,
            updated_at=None,
        )
        mock_repo.create.return_value = mock_grocery_item
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.create_grocery_item(name="Test Grocery Item")

        # Then
        assert result.name == "Test Grocery Item"
        assert result.quantity is None
        assert result.is_completed is False
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_grocery_item_when_get_by_id_called(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        mock_grocery_item = GroceryItem(
            id=1,
            name="Test Grocery Item",
            quantity="2 units",
            is_completed=False,
            created_at=None,
            updated_at=None,
        )
        mock_repo.get_by_id.return_value = mock_grocery_item
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.get_grocery_item(1)

        # Then
        assert result is not None
        assert result.id == 1
        assert result.name == "Test Grocery Item"
        mock_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_should_return_none_when_grocery_item_not_found(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        mock_repo.get_by_id.return_value = None
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.get_grocery_item(999)

        # Then
        assert result is None
        mock_repo.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_should_update_grocery_item_when_valid_data_provided(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        existing_grocery_item = GroceryItem(
            id=1,
            name="Old Grocery Item",
            quantity="1 unit",
            is_completed=False,
            created_at=None,
            updated_at=None,
        )
        updated_grocery_item = GroceryItem(
            id=1,
            name="Updated Grocery Item",
            quantity="2 units",
            is_completed=True,
            created_at=None,
            updated_at=None,
        )
        mock_repo.get_by_id.return_value = existing_grocery_item
        mock_repo.update.return_value = updated_grocery_item
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.update_grocery_item(
            grocery_item_id=1,
            name="Updated Grocery Item",
            quantity="2 units",
            is_completed=True,
        )

        # Then
        assert result is not None
        assert result.name == "Updated Grocery Item"
        assert result.quantity == "2 units"
        assert result.is_completed is True
        mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_update_grocery_item_partial_fields(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        existing_grocery_item = GroceryItem(
            id=1,
            name="Old Grocery Item",
            quantity="1 unit",
            is_completed=False,
            created_at=None,
            updated_at=None,
        )
        updated_grocery_item = GroceryItem(
            id=1,
            name="Updated Grocery Item",
            quantity="1 unit",
            is_completed=False,
            created_at=None,
            updated_at=None,
        )
        mock_repo.get_by_id.return_value = existing_grocery_item
        mock_repo.update.return_value = updated_grocery_item
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.update_grocery_item(
            grocery_item_id=1,
            name="Updated Grocery Item",
        )

        # Then
        assert result is not None
        assert result.name == "Updated Grocery Item"
        assert result.quantity == "1 unit"  # Should remain unchanged
        mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_none_when_update_nonexistent_grocery_item(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        mock_repo.get_by_id.return_value = None
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.update_grocery_item(
            grocery_item_id=999,
            name="Updated Grocery Item",
            quantity="2 units",
            is_completed=True,
        )

        # Then
        assert result is None
        mock_repo.get_by_id.assert_called_once_with(999)
        mock_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_delete_grocery_item_when_exists(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        mock_repo.delete.return_value = True
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.delete_grocery_item(1)

        # Then
        assert result is True
        mock_repo.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_should_return_false_when_delete_nonexistent_grocery_item(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        mock_repo.delete.return_value = False
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.delete_grocery_item(999)

        # Then
        assert result is False
        mock_repo.delete.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_no_grocery_items_exist(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        mock_repo.list_all.return_value = []
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.list_grocery_items()

        # Then
        assert result == []
        mock_repo.list_all.assert_called_once_with(skip=0, limit=100)

    @pytest.mark.asyncio
    async def test_should_return_grocery_items_when_list_called(self) -> None:
        # Given
        mock_repo = AsyncMock(spec=GroceryRepositoryImpl)
        mock_grocery_items = [
            GroceryItem(
                id=1,
                name="Grocery Item 1",
                quantity="2 units",
                is_completed=False,
                created_at=None,
                updated_at=None,
            ),
            GroceryItem(
                id=2,
                name="Grocery Item 2",
                quantity="500g",
                is_completed=True,
                created_at=None,
                updated_at=None,
            ),
        ]
        mock_repo.list_all.return_value = mock_grocery_items
        use_cases = GroceryUseCases(mock_repo)

        # When
        result = await use_cases.list_grocery_items(skip=0, limit=10)

        # Then
        assert len(result) == 2
        assert result[0].name == "Grocery Item 1"
        assert result[1].name == "Grocery Item 2"
        assert result[0].is_completed is False
        assert result[1].is_completed is True
        mock_repo.list_all.assert_called_once_with(skip=0, limit=10)
