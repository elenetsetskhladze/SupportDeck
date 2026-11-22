import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

CHECKPOINT_URL = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as db:
        yield db


class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def lifespan(app):
    from backend.security import create_default_admin
    from backend.agents import build_graph

    pool = AsyncConnectionPool(
        conninfo=CHECKPOINT_URL,
        min_size=1,
        max_size=10,
        kwargs={
            "row_factory": dict_row,
            "autocommit": True,
            "prepare_threshold": 0
        },
        open=False
    )

    try:
        await pool.open(wait=True)

        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

        app.state.graph = build_graph(checkpointer)

        await create_default_admin()

        yield

    finally:
        await pool.close()
        await engine.dispose()

