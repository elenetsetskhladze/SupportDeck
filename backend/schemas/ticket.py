from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class TicketCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=5000)

class TicketCreatedResponse(BaseModel):
    id: int
    status: str

class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    author_type: str
    author_id: int | None
    content: str
    created_at: datetime

class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    costumer_id: int
    subject: str
    body: str
    status: str
    category: str|None
    priority: str|None
    sentiment: str|None
    language: str|None
    ai_summary: str|None
    assigned_agent_id: int|None
    created_at: datetime
    updated_at: datetime

class TicketDetailResponse(TicketResponse):
    messages: list[MessageResponse] = []

