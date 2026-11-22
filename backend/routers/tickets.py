from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db, SessionLocal
from backend.models.user import User
from backend.models.ticket import Ticket
from backend.models.ticket_message import TicketMessage
from backend.schemas.ticket import TicketCreate, TicketCreatedResponse, TicketResponse, TicketDetailResponse, MessageCreate, MessageResponse
from backend.security import get_current_user

router = APIRouter(prefix="/tickets", tags=["tickets"])

MAX_TICKETS_PER_HOUR = 10


async def start_ai(graph, ticket_id: int, subject: str, body: str, costumer_email: str):
    config = {
        "configurable": {"thread_id": f"ticket-{ticket_id}"},
        "run_name": f"ticket-{ticket_id}",
        "tags": ["supportdesk", "triage"],
        "metadata": {"ticket_id": ticket_id}
    }

    try:
        await graph.ainvoke(
            {
                "ticket_id": ticket_id,
                "subject": subject,
                "body": body,
                "costumer_email": costumer_email
            },
            config
        )
    except Exception as error:
        print(f"AI failed for ticket {ticket_id}: {error}")

        async with SessionLocal() as db:
            ticket = await db.get(Ticket, ticket_id)
            ticket.status = "new"
            await db.commit()


@router.post("/", response_model=TicketCreatedResponse, status_code=201)
async def create_ticket(
        ticket: TicketCreate,
        background_tasks: BackgroundTasks,
        request: Request,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.role != "costumer":
        raise HTTPException(status_code=403)

    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    query = select(func.count(Ticket.id)).where(
        Ticket.costumer_id == current_user.id,
        Ticket.created_at >= one_hour_ago
    )

    tickets_count = await db.scalar(query)

    if tickets_count >= MAX_TICKETS_PER_HOUR:
        raise HTTPException(status_code=429)

    new_ticket = Ticket(
        costumer_id=current_user.id,
        subject=ticket.subject,
        body=ticket.body,
        status="triaging"
    )

    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)

    background_tasks.add_task(
        start_ai,
        request.app.state.graph,
        new_ticket.id,
        new_ticket.subject,
        new_ticket.body,
        current_user.email
    )

    return new_ticket

@router.get("/", response_model=list[TicketResponse])
async def get_tickets(
        status: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        sentiment: str | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 20,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    page = max(page, 1)
    size = min(size, 100)

    query = select(Ticket)

    if current_user.role == "costumer":
        query = query.where(Ticket.costumer_id == current_user.id)
    if status:
        query = query.where(Ticket.status == status)
    if category:
        query = query.where(Ticket.category == category)
    if priority:
        query = query.where(Ticket.priority == priority)
    if sentiment:
        query = query.where(Ticket.sentiment == sentiment)
    if search:
        pattern = f"%{search}%"
        query = query.where(or_(Ticket.subject.ilike(pattern), Ticket.body.ilike(pattern)))

    query = query.order_by(Ticket.created_at.desc())
    query = query.offset((page - 1) * size).limit(size)

    result = await db.scalars(query)

    return result.all()

@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
        ticket_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    ticket = await db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(status_code=404)
    if current_user.role == "costumer" and ticket.costumer_id != current_user.id:
        raise HTTPException(status_code=404)

    result = await db.scalars(
        select(TicketMessage).where(
            TicketMessage.ticket_id == ticket.id
        ).order_by(TicketMessage.created_at)
    )

    ticket_data = TicketResponse.model_validate(ticket).model_dump()
    ticket_data["messages"] = result.all()

    return ticket_data

@router.post("/{ticket_id}/messages", response_model=MessageResponse, status_code=201)
async def add_message(
        ticket_id: int,
        message: MessageCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    ticket = await db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(status_code=404)

    if current_user.role == "costumer" and ticket.costumer_id != current_user.id:
        raise HTTPException(status_code=404)

    if ticket.costumer_id != current_user.id:
        raise HTTPException(status_code=403)

    new_message = TicketMessage(
        ticket_id=ticket.id,
        author_type="costumer",
        author_id=current_user.id,
        content=message.content
    )

    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    return new_message
