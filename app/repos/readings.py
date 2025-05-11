from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models.db import ReadingDb
from .utils.super_repo import SuperRepo
from sqlalchemy import select


class ReadingRepository(SuperRepo[ReadingDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ReadingDb)

    async def get_by_device(self, device_id: int) -> List[ReadingDb]:
        result = await self.db.execute(select(self.model).where(self.model.device_id == device_id))
        return result.scalars().all()
