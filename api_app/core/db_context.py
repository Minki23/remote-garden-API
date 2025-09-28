from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from common_db.db import Base
from core.config import CONFIG

DB_URL = CONFIG.DB_CONNECTION_STRING

# Global async engine and session maker for database connections
async_engine = create_async_engine(DB_URL, echo=False)
async_session_maker = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_session() -> AsyncSession:
    """
    Dependency function that provides an async database session.

    Yields
    ------
    AsyncSession
        A SQLAlchemy async session, automatically closed after use.
    """
    async with async_session_maker() as session:
        yield session


async def create_async_tables():
    """
    Create all database tables asynchronously.

    Runs metadata creation for all models defined in the common DB Base.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
