from mappers.esp_devices import db_esp_to_dto
from models.dtos.esp_device import AssignGardenDTO, EspDeviceDTO
from repos.agents import AgentRepository
from repos.esp_devices import EspDeviceRepository
from repos.schedules import ScheduleRepository
from fastapi import Path, Body, Depends
from typing import Annotated, List

from exceptions.scheme import AppException
from models.enums import ScheduleActionType
from models.dtos.gardens import GardenDTO
from models.dtos.devices import DeviceDTO
from models.dtos.notifications import NotificationDTO
from models.dtos.schedules import WeeklyScheduleDTO
from models.db import AgentDb, EspDeviceDb, GardenDb, UserDb
from mappers.gardens import db_to_garden_dto
from mappers.devices import db_to_dto as db_device_to_dto
from mappers.notifications import db_to_dto as db_notification_to_dto
from repos.gardens import GardenRepository
from repos.devices import DeviceRepository
from repos.notifications import NotificationRepository
from repos.user_device import UserDeviceRepository
from services import (
    users,
    gardens,
    devices,
    notifications,
    readings,
    auth,
    esp_devices,
)
from services import agents
from services.agents import AgentService
from services.schedules import ScheduleService
from core.db_context import get_async_session
from core.security.deps import SubjectType, get_current_subject, get_current_user_id, get_current_admin_user, get_current_agent
from fastapi import Security

from services.user_devices import UserDeviceService

# --- Service Factories ---


async def _get_user_service(db=Depends(get_async_session)) -> users.UserService:
    return users.UserService(users.UserRepository(db))


async def _get_garden_service(db=Depends(get_async_session)) -> gardens.GardenService:
    return gardens.GardenService(
        gardens.GardenRepository(db), await _get_device_service(db)
    )


async def _get_device_service(db=Depends(get_async_session)) -> devices.DeviceService:
    return devices.DeviceService(devices.DeviceRepository(db))


async def _get_notification_service(
    db=Depends(get_async_session),
) -> notifications.NotificationService:
    return notifications.NotificationService(notifications.NotificationRepository(db))


async def _get_reading_service(
    db=Depends(get_async_session),
) -> readings.ReadingService:
    return readings.ReadingService(readings.ReadingRepository(db))


async def _get_auth_service(db=Depends(get_async_session)) -> auth.AuthService:
    return auth.AuthService(
        users.UserRepository(db)
    )


async def _get_esp_devices_service(
    db=Depends(get_async_session),
) -> esp_devices.EspDeviceService:
    return esp_devices.EspDeviceService(esp_devices.EspDeviceRepository(db), users.UserRepository(db))


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


async def _get_user_garden_or_404(db, garden_id: int, user_id: int) -> GardenDb:
    garden = await GardenRepository(db).get_by_id_and_user(garden_id, user_id)
    if not garden:
        raise AppException("Garden not found or access denied", 404)
    return garden


async def _get_agent_garden_or_404(db, garden_id: int, agent_id: int) -> GardenDb:
    agent = await AgentRepository(db).get_by_id(agent_id)
    if not agent.garden_id == garden_id:
        raise AppException("Garden not found or access denied", 404)
    return agent


async def _get_user_esp_or_404(db, esp_id: int, user_id: int) -> EspDeviceDb:
    esp = await EspDeviceRepository(db).get_by_id_and_user(esp_id, user_id)
    if not esp:
        raise AppException("ESP device not found or access denied", 404)
    return esp


async def _get_esp_device_for_garden(
    garden_id: int = Path(...),
    subject: tuple[int, SubjectType] = Depends(get_current_subject),
    db=Depends(get_async_session),
) -> List[EspDeviceDTO]:
    idd, subject_type = subject
    if subject_type == SubjectType.USER:
        await _get_user_garden_or_404(db, garden_id, idd)
    else:
        await _get_agent_garden_or_404(db, garden_id, idd)

    esp_repo = EspDeviceRepository(db)
    esp_devices = await esp_repo.get_by_garden_id(garden_id)
    if not esp_devices:
        raise AppException("No ESP device found for this garden", 404)

    return [db_esp_to_dto(esp_device) for esp_device in esp_devices]


async def _get_esp_device_for_id_in_garden(
    esp_id: int = Path(...),
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_async_session),
) -> EspDeviceDTO:
    esp_device = await _get_user_esp_or_404(db, esp_id, user_id)
    return db_esp_to_dto(esp_device)


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


async def _get_user_esp_and_garden(
    esp_id: int = Path(...),
    data: AssignGardenDTO = Body(...),
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_async_session),
) -> tuple[EspDeviceDTO, GardenDTO]:
    esp_repo = EspDeviceRepository(db)
    esp_device = await esp_repo.get_by_id(esp_id)
    if not esp_device or esp_device.garden and esp_device.garden.user_id != user_id:
        raise AppException("ESP device not found or access denied", 404)

    garden = await GardenRepository(db).get_by_id_and_user(data.garden_id, user_id)
    if not garden:
        raise AppException("Garden not found or access denied", 404)

    return db_esp_to_dto(esp_device), db_to_garden_dto(garden)


def _get_user_device_service(db=Depends(get_async_session),) -> UserDeviceService:
    return UserDeviceService(UserDeviceRepository(db))


async def _get_agent_service(db=Depends(get_async_session)) -> AgentService:
    return AgentService(AgentRepository(db))

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
GardenServiceDep = Annotated[gardens.GardenService,
                             Depends(_get_garden_service)]
DeviceServiceDep = Annotated[devices.DeviceService,
                             Depends(_get_device_service)]
NotificationServiceDep = Annotated[
    notifications.NotificationService, Depends(_get_notification_service)
]
ReadingServiceDep = Annotated[readings.ReadingService, Depends(
    _get_reading_service)]
ScheduleServiceDep = Annotated[ScheduleService, Depends(_get_schedule_service)]
AuthServiceDep = Annotated[auth.AuthService, Depends(_get_auth_service)]
EspDeviceServiceDep = Annotated[
    esp_devices.EspDeviceService, Depends(_get_esp_devices_service)
]
EspDeviceForGardenDep = Annotated[
    List[EspDeviceDTO], Depends(_get_esp_device_for_garden)
]
SpecificEspDeviceForGardenDep = Annotated[
    EspDeviceDTO, Depends(_get_esp_device_for_id_in_garden)
]

GardenDep = Annotated[GardenDTO, Depends(_get_garden_for_user)]
UserNotificationDep = Annotated[NotificationDTO,
                                Depends(_get_user_notification)]
UserDeviceDep = Annotated[DeviceDTO, Depends(_get_user_device)]
WeeklyCronDep = Annotated[
    tuple[str, ScheduleActionType], Depends(_convert_weekly_dto_to_cron)
]
CurrentUserDep = Annotated[int, Security(get_current_user_id)]
UserScheduleDep = Annotated[str, Depends(_get_user_schedule)]
AdminUserDep = Annotated[UserDb, Depends(get_current_admin_user)]
AgentDep = Annotated[AgentDb, Depends(get_current_agent)]
CurrentSubjectDep = Annotated[tuple[int,
                                    SubjectType], Depends(get_current_subject)]
UserEspAndGardenDep = Annotated[
    tuple[EspDeviceDTO, GardenDTO], Depends(_get_user_esp_and_garden)
]
UserDeviceServiceDep = Annotated[UserDeviceService, Depends(
    _get_user_device_service)]
AgentServiceDep = Annotated[AgentService, Depends(_get_agent_service)]
