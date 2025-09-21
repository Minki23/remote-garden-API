from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db import GardenDb
from .utils.super_repo import SuperRepo
from sqlalchemy import select


class GardenRepository(SuperRepo[GardenDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, GardenDb)

    async def get_all_by_user(self, user_id: int) -> List[GardenDb]:
        result = await self.db.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_id_and_user(self, garden_id: int, user_id: int) -> GardenDb | None:
        result = await self.db.execute(
            select(self.model).where(
                (self.model.id == garden_id) & (self.model.user_id == user_id)
            )
        )
        return result.scalars().first()
