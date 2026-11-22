import logging

from fastapi import FastAPI

from backend.database import lifespan
from backend.routers import auth, tickets, kb, analytics, review, orders

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="SupportDesk AI", lifespan=lifespan)

app.include_router(auth.router)

app.include_router(tickets.router)

app.include_router(kb.router)

app.include_router(analytics.router)

app.include_router(review.router)

app.include_router(orders.router)