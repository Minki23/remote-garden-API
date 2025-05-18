import asyncio
from app.core.db_context import create_async_tables

if __name__ == "__main__":
    asyncio.run(create_async_tables())
