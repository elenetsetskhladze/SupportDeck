from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class KBArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    category: Literal["billing", "technical", "account", "shipping", "general"]
    content: str = Field(min_length=1)
    is_published: bool = True


class KBArticleUpdate(BaseModel):
    title: str | None = None
    category: Literal["billing", "technical", "account", "shipping", "general"] | None = None
    content: str | None = None
    is_published: bool | None = None


class KBArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str
    content: str
    is_published: bool
    updated_at: datetime


class KBSearchRequest(BaseModel):
    query: str = Field(min_length=1)


class KBSearchResult(BaseModel):
    article_id: int
    title: str
    content: str
    score: float