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

    async def get_all_for_esp_mac(self, mac: str) -> List[DeviceDb]:
        result = await self.db.execute(
            select(DeviceDb)
            .join(EspDeviceDb, DeviceDb.esp_id == EspDeviceDb.id)
            .where(EspDeviceDb.mac == mac)
            .options(joinedload(DeviceDb.esp))
        )
        return result.scalars().all()

    async def get_device_by_type_for_esp_mac(
        self,
        mac: str,
        type: DeviceType
    ) -> DeviceDb | None:
        result = await self.db.execute(
            select(DeviceDb)
            .join(EspDeviceDb, DeviceDb.esp_id == EspDeviceDb.id)
            .where(
                EspDeviceDb.mac == mac,
                DeviceDb.type == type
            )
            .limit(1)
            .options(joinedload(DeviceDb.esp))
        )
        return result.scalar_one_or_none()

    async def get_all_for_esp_id(self, esp_id: int) -> List[DeviceDb]:
        stmt = select(DeviceDb).where(DeviceDb.esp_id == esp_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

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
