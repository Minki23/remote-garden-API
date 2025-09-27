from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from common_db.db import GardenDb
from .utils.super_repo import SuperRepo
from sqlalchemy import select


class GardenRepository(SuperRepo[GardenDb]):
    """
    Repository for managing `GardenDb` entities.
    Provides queries scoped to a specific user.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db, GardenDb)

    async def get_all_by_user(self, user_id: int) -> List[GardenDb]:
        """
        Fetch all gardens belonging to a given user.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_id_and_user(self, garden_id: int, user_id: int) -> GardenDb | None:
        """
        Fetch a garden by its ID, ensuring it belongs to the given user.
        Returns None if not found or not owned by the user.
        """
        result = await self.db.execute(
            select(self.model).where(
                (self.model.id == garden_id) & (self.model.user_id == user_id)
            )
        )
        return result.scalars().first()
