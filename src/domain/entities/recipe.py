from dataclasses import dataclass
from datetime import datetime


@dataclass
class Recipe:
    id: int | None = None
    title: str | None = None
    creation_date: datetime | None = None
    last_updated: datetime | None = None
    content: str | None = None
    summary: str | None = None
