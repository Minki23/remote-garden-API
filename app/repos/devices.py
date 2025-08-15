from typing import List
from app.models.dtos.esp_device import EspDeviceDTO
from app.models.enums import DeviceType
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db import DeviceDb, EspDeviceDb, GardenDb
from .utils.super_repo import SuperRepo
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class DeviceRepository(SuperRepo[DeviceDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DeviceDb)

    async def get_all_for_esps(self, esps: List[EspDeviceDTO]) -> list[DeviceDb]:
        esp_ids = [esp.id for esp in esps]
        result = await self.db.execute(
            select(DeviceDb)
            .where(DeviceDb.esp_id.in_(esp_ids))
            .options(joinedload(DeviceDb.esp))
        )
        return result.scalars().all()

    async def get_by_esp_id_and_type(
        self, esp_id: int, type: DeviceType
    ) -> DeviceDb | None:
        result = await self.db.execute(
            select(DeviceDb)
            .where(DeviceDb.esp_id == esp_id)
            .where(DeviceDb.type == type)
            .limit(1)
            .options(joinedload(DeviceDb.esp))
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_user(self, device_id: int, user_id: int) -> DeviceDb | None:
        result = await self.db.execute(
            select(DeviceDb)
            .join(DeviceDb.esp)
            .join(EspDeviceDb.garden)
            .where(DeviceDb.id == device_id)
            .where(GardenDb.user_id == user_id)
            .limit(1)
            .options(joinedload(DeviceDb.esp).joinedload(EspDeviceDb.garden))
        )
        return result.scalar_one_or_none()
