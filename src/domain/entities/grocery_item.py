from dataclasses import dataclass
from datetime import datetime


@dataclass
class GroceryItem:
    id: int | None = None
    name: str | None = None
    quantity: str | None = None
    is_completed: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
