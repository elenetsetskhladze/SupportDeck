from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=6, max_length=150)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    role: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class RoleUpdate(BaseModel):
    role: Literal["costumer", "agent", "admin"]