from typing import Literal

from pydantic import BaseModel, Field


class TriageResult(BaseModel):
    category: Literal["billing", "technical", "account", "shipping", "general", "spam"]
    priority: Literal["low", "medium", "high", "urgent"]
    sentiment: Literal["positive", "neutral", "negative", "angry"]
    language: str
    summary: str = Field(max_length=200)
    classification_confidence: float = Field(ge=0, le=1)


class DraftReply(BaseModel):
    draft_reply: str
    draft_confidence: float = Field(ge=0, le=1)
    cited_article_ids: list[int] = Field(default_factory=list)


class QualityCheckResult(BaseModel):
    is_acceptable: bool
    issues: list[str] = Field(default_factory=list)