from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from common_db.db import EspDeviceDb
from repos.utils.super_repo import SuperRepo
from typing import List, Optional


class EspDeviceRepository(SuperRepo[EspDeviceDb]):
    """
    Repository for managing `EspDeviceDb` entities.
    Provides queries to fetch ESP devices by user, client, MAC, or garden.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db, EspDeviceDb)

    async def get_by_user_id(self, user_id: int) -> List[EspDeviceDb]:
        """
        Fetch all ESP devices owned by a given user.
        """
        stmt = select(EspDeviceDb).where(EspDeviceDb.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_client(self, mac: str, client_secret: str) -> Optional[EspDeviceDb]:
        """
        Fetch a single ESP device by its MAC and client secret.
        Returns None if not found.
        """
        result = await self.db.execute(
            select(EspDeviceDb)
            .where(EspDeviceDb.mac == mac)
            .where(EspDeviceDb.secret == client_secret)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_mac(self, mac: str) -> Optional[EspDeviceDb]:
        """
        Fetch a single ESP device by its MAC address.
        Returns None if not found.
        """
        result = await self.db.execute(
            select(EspDeviceDb).where(EspDeviceDb.mac == mac).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_garden_id(self, garden_id: int) -> List[EspDeviceDb]:
        """
        Fetch all ESP devices linked to a specific garden.
        """
        result = await self.db.execute(
            select(EspDeviceDb).where(EspDeviceDb.garden_id == garden_id)
        )
        return result.scalars().all()

    async def get_by_id_and_user(self, esp_id: int, user_id: int) -> Optional[EspDeviceDb]:
        """
        Fetch a single ESP device by its ID and owner user ID.
        Returns None if not found or user does not own the device.
        """
        result = await self.db.execute(
            select(EspDeviceDb)
            .where(EspDeviceDb.id == esp_id)
            .where(EspDeviceDb.user_id == user_id)
            .limit(1)
        )
        return result.scalar_one_or_none()
