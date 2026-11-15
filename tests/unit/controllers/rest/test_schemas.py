import pytest

from src.controllers.rest.schemas import GroceryItemCreate, GroceryItemUpdate


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
