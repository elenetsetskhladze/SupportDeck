from fastapi import APIRouter, Depends, HTTPException, Request
from langgraph.types import Command
from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.user import User
from backend.models.ticket import Ticket
from backend.schemas.ticket import TicketResponse
from backend.schemas.review import ReviewDecision, ReviewResponse, ReviewDetailResponse
from backend.security import require_agent

router = APIRouter(prefix="/review", tags=["review"])

@router.get("/queue", response_model=list[TicketResponse])
async def get_queue(
        current_user: User = Depends(require_agent),
        db: AsyncSession = Depends(get_db)
):
    priority_order = case(
        {"urgent": 1, "high": 2, "medium": 3, "low": 4},
        value=Ticket.priority,
        else_=5
    )

    result = await db.scalars(
        select(Ticket).where(Ticket.status == "awaiting_review").order_by(priority_order, Ticket.created_at)
    )

    return result.all()

@router.get("/{ticket_id}", response_model=ReviewDetailResponse)
async def get_review(
        ticket_id: int,
        request: Request,
        current_user: User = Depends(require_agent),
        db: AsyncSession = Depends(get_db)
):
    ticket = await db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    config = {"configurable": {"thread_id": f"ticket-{ticket_id}"}}
    state = await request.app.state.graph.aget_state(config)
    values = state.values

    return {
        "ticket": ticket,
        "draft_reply": values.get("draft_reply", ""),
        "classification_confidence": values.get("classification_confidence"),
        "draft_confidence": values.get("draft_confidence"),
        "cited_article_ids": values.get("cited_article_ids", [])
    }

@router.post("/{ticket_id}/decision", response_model=ReviewResponse)
async def make_decision(
        ticket_id: int,
        review: ReviewDecision,
        request: Request,
        current_user: User = Depends(require_agent),
        db: AsyncSession = Depends(get_db)
):
    ticket = await db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.status != "awaiting_review":
        raise HTTPException(status_code=409, detail="Ticket is not waiting for review")
    if review.decision == "edit" and not (review.edited_reply or "").strip():
        raise HTTPException(status_code=400, detail="Edited reply cannot be empty")

    ticket.assigned_agent_id = current_user.id
    await db.commit()

    config = {
        "configurable": {"thread_id": f"ticket-{ticket_id}"},
        "run_name": f"ticket-{ticket_id}-review",
        "tags": ["supportdesk", "human-review"],
        "metadata": {
            "ticket_id": ticket_id,
            "reviewer_id": current_user.id,
            "decision": review.decision
        }
    }

    await request.app.state.graph.ainvoke(
        Command(resume={**review.model_dump(), "reviewer_id": current_user.id}),
        config
    )

    await db.refresh(ticket)

    return {
        "ticket_id": ticket.id,
        "decision": review.decision,
        "edited_reply": review.edited_reply,
        "comment": review.comment,
        "status": ticket.status
    }