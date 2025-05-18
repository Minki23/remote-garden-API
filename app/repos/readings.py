from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db import ReadingDb
from .utils.super_repo import SuperRepo
from sqlalchemy import select
from datetime import datetime
from sqlalchemy import and_, desc
from app.models.enums import DeviceType
from app.models.db import DeviceDb


class ReadingRepository(SuperRepo[ReadingDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ReadingDb)

    async def get_by_device(self, device_id: int) -> List[ReadingDb]:
        result = await self.db.execute(select(self.model).where(self.model.device_id == device_id))
        return result.scalars().all()

    async def get_by_garden_filters(
        self,
        garden_id: int,
        type: DeviceType,
        start_time: datetime,
        end_time: datetime,
    ) -> List[ReadingDb]:
        result = await self.db.execute(
            select(ReadingDb)
            .join(DeviceDb, ReadingDb.device_id == DeviceDb.id)
            .where(
                and_(
                    DeviceDb.garden_id == garden_id,
                    DeviceDb.type == type,
                    ReadingDb.timestamp >= start_time,
                    ReadingDb.timestamp <= end_time,
                )
            )
        )
        return result.scalars().all()

    async def get_last_for_garden_device_type(
        self, garden_id: int, type: DeviceType
    ) -> ReadingDb | None:
        result = await self.db.execute(
            select(ReadingDb)
            .join(DeviceDb, ReadingDb.device_id == DeviceDb.id)
            .where(
                and_(
                    DeviceDb.garden_id == garden_id,
                    DeviceDb.type == type,
                )
            )
            .order_by(desc(ReadingDb.timestamp))
            .limit(1)
        )
        return result.scalars().first()
