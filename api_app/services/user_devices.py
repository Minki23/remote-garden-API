from typing import Optional
from datetime import datetime
from common_db.db import UserDeviceDb
from repos.user_device import UserDeviceRepository


class UserDeviceService:
    """
    Service for managing user devices and their FCM tokens.

    Provides methods for registering, retrieving, and removing user devices.
    """

    def __init__(self, repo: UserDeviceRepository):
        """
        Initialize the service with a user device repository.
        """
        self.repo = repo

    async def register_device(
        self, user_id: int, fcm_token: str, platform: Optional[str]
    ) -> UserDeviceDb:
        """
        Register a new device or update an existing one.

        If a device with the same FCM token already exists, it will be updated
        with the provided user and platform. Otherwise, a new record is created.

        Parameters
        ----------
        user_id : int
            ID of the user who owns the device.
        fcm_token : str
            Firebase Cloud Messaging token identifying the device.
        platform : Optional[str]
            Device platform (e.g., "android", "ios"), if provided.

        Returns
        -------
        UserDeviceDb
            The registered or updated device record.
        """
        device = await self.repo.get_by_fcm_token(fcm_token)
        if device:
            device.user_id = user_id
            device.platform = platform
            device.last_seen = datetime.utcnow()
            return await self.repo.update(
                device.id, user_id=user_id, platform=platform, last_seen=device.last_seen
            )

        return await self.repo.create(
            user_id=user_id, fcm_token=fcm_token, platform=platform
        )

    async def get_user_tokens(self, user_id: int) -> list[str]:
        """
        Retrieve all FCM tokens for a given user.

        Parameters
        ----------
        user_id : int
            ID of the user.

        Returns
        -------
        list of str
            List of FCM tokens belonging to the user.
        """
        devices = await self.repo.get_by_user_id(user_id)
        return [d.fcm_token for d in devices]

    async def remove_device(self, fcm_token: str) -> bool:
        """
        Remove a device by its FCM token.

        Parameters
        ----------
        fcm_token : str
            Firebase Cloud Messaging token identifying the device.

        Returns
        -------
        bool
            True if the device was deleted, False if no matching device was found.
        """
        device = await self.repo.get_by_fcm_token(fcm_token)
        if not device:
            return False
        return await self.repo.delete(device.id)
