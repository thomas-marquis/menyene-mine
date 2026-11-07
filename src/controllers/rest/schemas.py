from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class RecipeCreate(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    summary: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class RecipeUpdate(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    summary: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class RecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    creation_date: datetime
    last_updated: datetime
    content: str
    summary: str


class RecipeListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recipes: list[RecipeResponse]
    total: int
    skip: int
    limit: int
