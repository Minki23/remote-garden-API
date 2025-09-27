from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from common_db.db import ReadingDb, DeviceDb, EspDeviceDb
from .utils.super_repo import SuperRepo
from sqlalchemy import select, and_, desc
from datetime import datetime
from common_db.enums import DeviceType


class ReadingRepository(SuperRepo[ReadingDb]):
    """
    Repository for managing `ReadingDb` entities.
    Provides queries filtered by garden, device type, and time ranges.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db, ReadingDb)

    async def get_last_for_garden_device_type(
        self, garden_id: int, type: DeviceType
    ) -> ReadingDb | None:
        """
        Fetch the most recent reading for a given garden and device type.
        Returns None if no reading exists.
        """
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
        """
        Fetch readings for a given garden and device type within a time range,
        ordered by newest first, with pagination (offset + limit).
        """
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
