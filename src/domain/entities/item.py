from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Item:
    id: str | UUID | None = None
    name: str | None = None
    created_at: datetime | None = None
