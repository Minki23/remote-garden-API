from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db import DeviceDb
from .utils.super_repo import SuperRepo
from sqlalchemy import select


class DeviceRepository(SuperRepo[DeviceDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DeviceDb)

    async def get_all_by_garden_id(self, garden_id: int) -> list[DeviceDb]:
        result = await self.db.execute(select(DeviceDb).where(DeviceDb.garden_id == garden_id))
        return result.scalars().all()
