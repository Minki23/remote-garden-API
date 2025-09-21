from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.db import Base
from app.core.config import CONFIG

DB_URL = CONFIG.DB_CONNECTION_STRING

async_engine = create_async_engine(DB_URL, echo=False)
async_session_maker = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def create_async_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
