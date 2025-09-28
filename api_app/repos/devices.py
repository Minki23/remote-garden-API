from typing import List
from models.dtos.esp_device import EspDeviceDTO
from common_db.enums import DeviceType
from sqlalchemy.ext.asyncio import AsyncSession
from common_db.db import DeviceDb, EspDeviceDb, GardenDb
from .utils.super_repo import SuperRepo
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class DeviceRepository(SuperRepo[DeviceDb]):
    """
    Repository for managing `DeviceDb` entities.
    Provides queries for devices filtered by ESP and user context.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db, DeviceDb)

    async def get_all_for_esps(self, esps: List[EspDeviceDTO]) -> list[DeviceDb]:
        """
        Fetch all devices linked to a list of ESPs.
        """
        esp_ids = [esp.id for esp in esps]
        result = await self.db.execute(
            select(DeviceDb)
            .where(DeviceDb.esp_id.in_(esp_ids))
            .options(joinedload(DeviceDb.esp))
        )
        return result.scalars().all()

    async def get_all_for_esp_mac(self, mac: str) -> List[DeviceDb]:
        """
        Fetch all devices associated with a specific ESP by MAC address.
        """
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
        """
        Fetch a single device of a given type for an ESP identified by MAC.
        Returns None if not found.
        """
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

    async def get_by_id_and_user(self, device_id: int, user_id: int) -> DeviceDb | None:
        """
        Fetch a device by its ID, validating that it belongs to a given user.
        Returns None if no match exists.
        """
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
