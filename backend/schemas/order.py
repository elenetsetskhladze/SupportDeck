from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    costumer_id: int
    product: str
    total: float
    status: str
    tracking_number: str | None
    created_at: datetime


class OrderUpdate(BaseModel):
    status: Literal["paid", "shipped", "delivered", "cancelled", "refunded"]
    tracking_number: str | None = None




class OrderCreate(BaseModel):
    product: str


class ProductResponse(BaseModel):
    name: str
    price: float