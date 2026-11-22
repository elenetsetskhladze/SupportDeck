from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base

class TriageRun(Base):
    __tablename__ = 'triage_runs'

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str | None] = mapped_column(String(30))
    priority: Mapped[str | None] = mapped_column(String(30))
    sentiment: Mapped[str | None] = mapped_column(String(30))
    classification_confidence: Mapped[float | None] = mapped_column(Float)
    draft_confidence: Mapped[float | None] = mapped_column(Float)
    route: Mapped[str | None] = mapped_column(String(30))
    human_decision: Mapped[str | None] = mapped_column(String(20))
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    langsmith_run_url: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)