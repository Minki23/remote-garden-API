from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db import UserDb
from .utils.super_repo import SuperRepo
from sqlalchemy.future import select

class UserRepository(SuperRepo[UserDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, UserDb)

    async def get_by_google_sub(self, sub: str) -> Optional[UserDb]:
        result = await self.db.execute(
            select(self.model).where(self.model.google_sub == sub)
        )
        return result.scalar_one_or_none()