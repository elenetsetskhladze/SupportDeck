from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, cast, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.user import User
from backend.models.order import Order
from backend.schemas.order import OrderResponse, OrderUpdate, OrderCreate, ProductResponse
from backend.products import PHONES
from backend.security import get_current_user, require_agent

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/products", response_model=list[ProductResponse])
async def get_products():
    return [{"name": name, "price": price} for name, price in PHONES.items()]


@router.post("", response_model=OrderResponse, status_code=201)
async def buy_product(data: OrderCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.product not in PHONES:
        raise HTTPException(status_code=400, detail="Product not found")

    last_number = await db.scalar(select(func.max(cast(Order.order_number, Integer))))

    order = Order(
        order_number=str((last_number or 1000) + 1),
        costumer_id=current_user.id,
        product=data.product,
        total=PHONES[data.product],
        status="paid"
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


@router.get("/my", response_model=list[OrderResponse])
async def get_my_orders(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.scalars(
        select(Order)
        .where(Order.costumer_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    return result.all()


@router.get("", response_model=list[OrderResponse])
async def get_all_orders(current_user: User = Depends(require_agent), db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(Order).order_by(Order.created_at.desc()))
    return result.all()


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(order_id: int, data: OrderUpdate, current_user: User = Depends(require_agent), db: AsyncSession = Depends(get_db)):
    order = await db.get(Order, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = data.status
    if data.tracking_number is not None:
        order.tracking_number = data.tracking_number

    await db.commit()
    await db.refresh(order)
    return order