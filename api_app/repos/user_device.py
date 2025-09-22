from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from models.db import UserDeviceDb
from repos.utils.super_repo import SuperRepo


class UserDeviceRepository(SuperRepo[UserDeviceDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, UserDeviceDb)

    async def get_by_fcm_token(self, token: str) -> Optional[UserDeviceDb]:
        result = await self.db.execute(
            select(UserDeviceDb).where(UserDeviceDb.fcm_token == token)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> list[UserDeviceDb]:
        result = await self.db.execute(
            select(UserDeviceDb).where(UserDeviceDb.user_id == user_id)
        )
        return result.scalars().all()
