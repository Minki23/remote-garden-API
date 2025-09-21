from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db import ReadingDb, DeviceDb, EspDeviceDb
from .utils.super_repo import SuperRepo
from sqlalchemy import select, and_, desc
from datetime import datetime
from app.models.enums import DeviceType


class ReadingRepository(SuperRepo[ReadingDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ReadingDb)

    async def get_last_for_garden_device_type(
        self, garden_id: int, type: DeviceType
    ) -> ReadingDb | None:
        result = await self.db.execute(
            select(ReadingDb)
            .join(DeviceDb, ReadingDb.device_id == DeviceDb.id)
            .join(EspDeviceDb, DeviceDb.esp_id == EspDeviceDb.id)
            .where(
                and_(
                    EspDeviceDb.garden_id == garden_id,
                    DeviceDb.type == type,
                )
            )
            .order_by(desc(ReadingDb.timestamp))
            .limit(1)
        )
        return result.scalars().first()

    async def get_by_garden_filters_paginated(
        self,
        garden_id: int,
        type: DeviceType,
        start_time: datetime,
        end_time: datetime,
        offset: int,
        limit: int,
    ) -> List[ReadingDb]:
        result = await self.db.execute(
            select(ReadingDb)
            .join(DeviceDb, ReadingDb.device_id == DeviceDb.id)
            .join(EspDeviceDb, DeviceDb.esp_id == EspDeviceDb.id)
            .where(
                and_(
                    EspDeviceDb.garden_id == garden_id,
                    DeviceDb.type == type,
                    ReadingDb.timestamp >= start_time,
                    ReadingDb.timestamp <= end_time,
                )
            )
            .order_by(desc(ReadingDb.timestamp))
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
