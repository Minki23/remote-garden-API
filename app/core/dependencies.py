from typing import Annotated
from fastapi import Depends

from app.services import users, gardens, devices, notifications, readings
from app.core.db_context import get_async_session
from core.security.auth import get_current_user_id


def _get_user_service(db=Depends(get_async_session)) -> users.UserService:
    return users.UserService(users.UserRepository(db))


def _get_garden_service(db=Depends(get_async_session)) -> gardens.GardenService:
    return gardens.GardenService(gardens.GardenRepository(db))


def _get_device_service(db=Depends(get_async_session)) -> devices.DeviceService:
    return devices.DeviceService(devices.DeviceRepository(db))


def _get_notification_service(db=Depends(get_async_session)) -> notifications.NotificationService:
    return notifications.NotificationService(notifications.NotificationRepository(db))


def _get_reading_service(db=Depends(get_async_session)) -> readings.ReadingService:
    return readings.ReadingService(readings.ReadingRepository(db))


UserServiceDep = Annotated[users.UserService, Depends(_get_user_service)]
GardenServiceDep = Annotated[gardens.GardenService, Depends(_get_garden_service)]
DeviceServiceDep = Annotated[devices.DeviceService, Depends(_get_device_service)]
NotificationServiceDep = Annotated[
    notifications.NotificationService, Depends(_get_notification_service)
]
ReadingServiceDep = Annotated[readings.ReadingService, Depends(_get_reading_service)]
CurrentUserDep = Annotated[int, Depends(get_current_user_id)]
