from dataclasses import dataclass
from datetime import datetime


@dataclass
class Recipe:
    """
    Recipe domain entity.

    Represents a complete recipe with all required fields.
    This is a pure domain object with no external dependencies.
    """

    id: int | None = None
    title: str | None = None
    creation_date: datetime | None = None
    last_updated: datetime | None = None
    content: str | None = None
    summary: str | None = None
