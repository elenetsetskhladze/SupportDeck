from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.user import User
from backend.models.ticket import Ticket
from backend.models.triage_run import TriageRun
from backend.security import require_admin

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def overview(
        current_user: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    total = await db.scalar(select(func.count(Ticket.id)))

    categories = await db.execute(
        select(Ticket.category, func.count(Ticket.id)).group_by(Ticket.category)
    )

    priorities = await db.execute(
        select(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority)
    )

    return {
        "total_tickets": total,
        "by_category": {category or "unclassified": count for category, count in categories},
        "by_priority": {priority or "unclassified": count for priority, count in priorities}
    }


@router.get("/automation-rate")
async def automation_rate(
        current_user: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TriageRun.route, func.count(TriageRun.id)).group_by(TriageRun.route)
    )

    counts = {route: count for route, count in result if route}

    auto_sent = counts.get("auto_sent", 0)
    human_review = counts.get("human_review", 0)

    return {
        "auto_sent": auto_sent,
        "human_review": human_review,
        "spam": counts.get("spam", 0),
        "automation_rate_percent": round(auto_sent / (auto_sent + human_review) * 100, 1)
        if auto_sent + human_review else 0
    }


@router.get("/ai-accuracy")
async def ai_accuracy(
        current_user: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TriageRun.human_decision, func.count(TriageRun.id))
        .where(TriageRun.human_decision.is_not(None))
        .group_by(TriageRun.human_decision)
    )

    counts = {decision: count for decision, count in result}

    avg_confidence = await db.scalar(select(func.avg(TriageRun.draft_confidence)))

    return {
        "approve": counts.get("approve", 0),
        "edit": counts.get("edit", 0),
        "reject": counts.get("reject", 0),
        "avg_draft_confidence": round(avg_confidence, 2) if avg_confidence is not None else None
    }