from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from models.db import NotificationDb
from .utils.super_repo import SuperRepo

from sqlalchemy import update


class NotificationRepository(SuperRepo[NotificationDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, NotificationDb)

    async def get_by_user(self, user_id: int) -> List[NotificationDb]:
        result = await self.db.execute(
            select(NotificationDb).where(NotificationDb.user_id == user_id)
        )
        return result.scalars().all()

    async def mark_as_read(self, notification_id: int) -> bool:
        result = await self.db.execute(
            update(NotificationDb)
            .where(NotificationDb.id == notification_id)
            .values(read=True)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.commit()
        return result.rowcount > 0

    async def get_by_user_and_type(
        self, user_id: int, type_: str
    ) -> List[NotificationDb]:
        result = await self.db.execute(
            select(NotificationDb).where(
                NotificationDb.user_id == user_id, NotificationDb.type == type_
            )
        )
        return result.scalars().all()

    async def get_by_id_and_user(
        self, notification_id: int, user_id: int
    ) -> NotificationDb | None:
        result = await self.db.execute(
            select(NotificationDb).where(
                NotificationDb.id == notification_id, NotificationDb.user_id == user_id
            )
        )
        return result.scalars().first()
