from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List

from common_db.db import NotificationDb
from .utils.super_repo import SuperRepo


class NotificationRepository(SuperRepo[NotificationDb]):
    """
    Repository for managing `NotificationDb` entities.
    Provides queries and updates scoped to a specific user.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db, NotificationDb)

    async def get_by_user(self, user_id: int) -> List[NotificationDb]:
        """
        Fetch all notifications belonging to the given user.
        """
        result = await self.db.execute(
            select(NotificationDb).where(NotificationDb.user_id == user_id)
        )
        return result.scalars().all()

    async def mark_as_read(self, notification_id: int) -> bool:
        """
        Mark a notification as read by its ID.
        Returns True if the row was updated, False otherwise.
        """
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
        """
        Fetch all notifications of a given type for the specified user.
        """
        result = await self.db.execute(
            select(NotificationDb).where(
                NotificationDb.user_id == user_id, NotificationDb.type == type_
            )
        )
        return result.scalars().all()

    async def get_by_id_and_user(
        self, notification_id: int, user_id: int
    ) -> NotificationDb | None:
        """
        Fetch a notification by ID, ensuring it belongs to the given user.
        Returns None if not found or not owned by the user.
        """
        result = await self.db.execute(
            select(NotificationDb).where(
                NotificationDb.id == notification_id, NotificationDb.user_id == user_id
            )
        )
        return result.scalars().first()
