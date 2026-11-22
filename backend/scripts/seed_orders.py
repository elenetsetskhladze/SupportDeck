import asyncio

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models.user import User
from backend.models.order import Order
from backend.security import hash_password

USERS = [
    {"email": "nino@gmail.com", "full_name": "Nino Beridze", "password": "nino12345"},
    {"email": "giorgi@gmail.com", "full_name": "Giorgi Kapanadze", "password": "giorgi12345"},
]

ORDERS = [
    {"order_number": "1001", "email": "nino@gmail.com", "product": "Aurora 12 Pro, 256 GB, Graphite", "total": 2899, "status": "shipped", "tracking_number": "GE123456"},
    {"order_number": "1002", "email": "nino@gmail.com", "product": "Volt Mini, 128 GB, Coral", "total": 999, "status": "paid", "tracking_number": None},
    {"order_number": "1003", "email": "nino@gmail.com", "product": "Echo Lite, 64 GB, Ivory", "total": 649, "status": "delivered", "tracking_number": "GE654321"},
    {"order_number": "1004", "email": "nino@gmail.com", "product": "Nimbus S, 128 GB, Sage", "total": 1499, "status": "cancelled", "tracking_number": None},
    {"order_number": "1005", "email": "giorgi@gmail.com", "product": "Lumen Fold, 512 GB, Sand", "total": 4299, "status": "shipped", "tracking_number": "GE777888"},
]


async def main():
    async with SessionLocal() as db:
        for data in USERS:
            existing = await db.scalar(select(User).where(User.email == data["email"]))

            if existing:
                print(f"User already exists: {data['email']}")
                continue

            user = User(
                email=data["email"],
                full_name=data["full_name"],
                hashed_password=hash_password(data["password"]),
                role="costumer"
            )
            db.add(user)
            await db.commit()
            print(f"Added user: {data['email']}")

        for data in ORDERS:
            existing = await db.scalar(select(Order).where(Order.order_number == data["order_number"]))

            if existing:
                print(f"Order already exists: #{data['order_number']}")
                continue

            user = await db.scalar(select(User).where(User.email == data["email"]))

            order = Order(
                order_number=data["order_number"],
                costumer_id=user.id,
                product=data["product"],
                total=data["total"],
                status=data["status"],
                tracking_number=data["tracking_number"]
            )
            db.add(order)
            await db.commit()
            print(f"Added order: #{data['order_number']}")


if __name__ == "__main__":
    asyncio.run(main())