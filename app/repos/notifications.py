from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from models.db import NotificationDb
from .utils.super_repo import SuperRepo


class NotificationRepository(SuperRepo[NotificationDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, NotificationDb)

    async def get_by_user(self, user_id: int) -> List[NotificationDb]:
        result = await self.db.execute(
            select(NotificationDb).where(NotificationDb.user_id == user_id)
        )
        return result.scalars().all()
