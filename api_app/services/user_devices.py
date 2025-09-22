from typing import Optional
from datetime import datetime
from models.db import UserDeviceDb
from repos.user_device import UserDeviceRepository


class UserDeviceService:
    def __init__(self, repo: UserDeviceRepository):
        self.repo = repo

    async def register_device(self, user_id: int, fcm_token: str, platform: Optional[str]) -> UserDeviceDb:
        device = await self.repo.get_by_fcm_token(fcm_token)
        if device:
            device.user_id = user_id
            device.platform = platform
            device.last_seen = datetime.utcnow()
            return await self.repo.update(device.id, user_id=user_id, platform=platform, last_seen=device.last_seen)

        return await self.repo.create(user_id=user_id, fcm_token=fcm_token, platform=platform)

    async def get_user_tokens(self, user_id: int) -> list[str]:
        devices = await self.repo.get_by_user_id(user_id)
        return [d.fcm_token for d in devices]

    async def remove_device(self, fcm_token: str) -> bool:
        device = await self.repo.get_by_fcm_token(fcm_token)
        if not device:
            return False
        return await self.repo.delete(device.id)
