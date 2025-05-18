from app.core.celery.celery_app import celery_app
from app.repos.schedules import ScheduleRepository
from fastapi import Path, Body, Depends
from typing import Annotated
from redis import Redis
from sqlalchemy import select

from app.exceptions.scheme import AppException
from app.models.enums import ScheduleActionType
from app.models.dtos.gardens import GardenDTO
from app.models.dtos.devices import DeviceDTO
from app.models.dtos.notifications import NotificationDTO
from app.models.dtos.schedules import WeeklyScheduleDTO
from app.models.db import DeviceDb, GardenDb
from app.mappers.gardens import db_to_garden_dto
from app.mappers.devices import db_to_dto as db_device_to_dto
from app.mappers.notifications import db_to_dto as db_notification_to_dto
from app.repos.gardens import GardenRepository
from app.repos.devices import DeviceRepository
from app.repos.notifications import NotificationRepository
from app.services import users, gardens, devices, notifications, readings, status
from app.services.schedules import ScheduleService
from app.core.db_context import get_async_session
from app.core.security.auth import get_current_user_id

# --- Service Factories ---


async def _get_user_service(db=Depends(get_async_session)) -> users.UserService:
    return users.UserService(users.UserRepository(db))


async def _get_garden_service(db=Depends(get_async_session)) -> gardens.GardenService:
    return gardens.GardenService(gardens.GardenRepository(db), await _get_device_service(db))


async def _get_device_service(db=Depends(get_async_session)) -> devices.DeviceService:
    return devices.DeviceService(devices.DeviceRepository(db))


async def _get_notification_service(
    db=Depends(get_async_session),
) -> notifications.NotificationService:
    return notifications.NotificationService(notifications.NotificationRepository(db))


async def _get_reading_service(db=Depends(get_async_session)) -> readings.ReadingService:
    return readings.ReadingService(readings.ReadingRepository(db))


async def _get_status_service() -> status.StatusService:
    return status.StatusService()


# _redis_client = Redis(host="redis", port=6379, decode_responses=True)


async def _get_schedule_service() -> ScheduleService:
    return ScheduleService(ScheduleRepository())


# --- Domain Object Deps ---


async def _get_garden_for_user(
    garden_id: int = Path(...),
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_async_session),
) -> GardenDTO:
    garden = await GardenRepository(db).get_by_id_and_user(garden_id, user_id)
    if not garden:
        raise AppException("Garden not found or access denied", 404)
    return db_to_garden_dto(garden)


async def _get_user_notification(
    id: int,
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_async_session),
) -> NotificationDTO:
    repo = NotificationRepository(db)
    notif = await repo.get_by_id_and_user(id, user_id)
    if not notif:
        raise AppException("Notification not found or access denied", 404)
    return db_notification_to_dto(notif)


async def _get_user_device(
    device_id: int,
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_async_session),
) -> DeviceDTO:
    repo = DeviceRepository(db)
    device = await repo.get_by_id_and_user(device_id, user_id)
    if not device:
        raise AppException("Device not found or access denied", 404)
    return db_device_to_dto(device)


async def _get_user_schedule(
    task_id: str,
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_async_session),
) -> str:
    service = await _get_schedule_service()
    garden_id = service.get_garden_id(task_id)
    garden = await GardenRepository(db).get_by_id_and_user(garden_id, user_id)
    if not garden:
        raise AppException("Schedule not found or access denied", 404)
    return task_id


# --- Conversion Deps ---

_WEEKDAY_MAP = {
    "mon": "1",
    "tue": "2",
    "wed": "3",
    "thu": "4",
    "fri": "5",
    "sat": "6",
    "sun": "0",
}


async def _convert_weekly_dto_to_cron(
    dto: WeeklyScheduleDTO = Body(...),
) -> tuple[str, ScheduleActionType]:
    day_nums = [_WEEKDAY_MAP[day] for day in dto.days_of_week]
    day_str = ",".join(day_nums)
    cron = f"{dto.minute} {dto.hour} * * {day_str}"
    return cron, dto.action


# --- Annotated Dependencies ---

UserServiceDep = Annotated[users.UserService, Depends(_get_user_service)]
GardenServiceDep = Annotated[gardens.GardenService, Depends(_get_garden_service)]
DeviceServiceDep = Annotated[devices.DeviceService, Depends(_get_device_service)]
NotificationServiceDep = Annotated[
    notifications.NotificationService, Depends(_get_notification_service)
]
ReadingServiceDep = Annotated[readings.ReadingService, Depends(_get_reading_service)]
StatusServiceDep = Annotated[status.StatusService, Depends(_get_status_service)]
ScheduleServiceDep = Annotated[ScheduleService, Depends(_get_schedule_service)]

GardenDep = Annotated[GardenDTO, Depends(_get_garden_for_user)]
UserNotificationDep = Annotated[NotificationDTO, Depends(_get_user_notification)]
UserDeviceDep = Annotated[DeviceDTO, Depends(_get_user_device)]
WeeklyCronDep = Annotated[tuple[str, ScheduleActionType], Depends(_convert_weekly_dto_to_cron)]
CurrentUserDep = Annotated[int, Depends(get_current_user_id)]
UserScheduleDep = Annotated[str, Depends(_get_user_schedule)]
