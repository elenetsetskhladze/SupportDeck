from typing import Literal

from pydantic import BaseModel

from backend.schemas.ticket import TicketResponse


class ReviewDecision(BaseModel):
    decision: Literal["approve", "edit", "reject"]
    edited_reply: str | None = None
    comment: str | None = None


class ReviewResponse(BaseModel):
    ticket_id: int
    decision: str
    status: str


class ReviewDetailResponse(BaseModel):
    ticket: TicketResponse
    draft_reply: str | None
    classification_confidence: float | None
    draft_confidence: float | None
    cited_article_ids: list[int]
