import asyncio

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models.user import User
from backend.models.order import Order
from backend.products import PHONES
from backend.security import hash_password

USERS = [
    {"email": "nino@gmail.com", "full_name": "Nino Beridze", "password": "nino12345"},
    {"email": "giorgi@gmail.com", "full_name": "Giorgi Kapanadze", "password": "giorgi12345"},
]

ORDERS = [
    {"order_number": "1001", "email": "nino@gmail.com", "product": "iPhone 17 Pro", "status": "shipped", "tracking_number": "GE123456"},
    {"order_number": "1002", "email": "nino@gmail.com", "product": "Samsung Galaxy S26 Ultra", "status": "paid", "tracking_number": None},
    {"order_number": "1003", "email": "nino@gmail.com", "product": "iPhone 16", "status": "delivered", "tracking_number": "GE654321"},
    {"order_number": "1004", "email": "nino@gmail.com", "product": "Samsung Galaxy Z Flip8", "status": "cancelled", "tracking_number": None},
    {"order_number": "1005", "email": "giorgi@gmail.com", "product": "Samsung Galaxy Z Fold8", "status": "shipped", "tracking_number": "GE777888"},
    {"order_number": "1006", "email": "nino@gmail.com", "product": "iPhone 18 Pro Max", "status": "paid", "tracking_number": None},
    {"order_number": "1007", "email": "giorgi@gmail.com", "product": "iPhone 15 Pro", "status": "delivered", "tracking_number": "GE555111"},
]


async def main():
    async with SessionLocal() as db:
        for data in ARTICLES:
            existing = await db.scalar(select(KBArticle).where(KBArticle.title == data["title"]))

            if existing:
                print(f"Already exists: {data['title']}")
                continue

            article = KBArticle(**data)
            db.add(article)
            await db.commit()
            await db.refresh(article)

            await index_article(article, db)
            print(f"Added: {article.title}")


if __name__ == "__main__":
    asyncio.run(main())