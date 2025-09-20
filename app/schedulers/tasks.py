from app.core.celery.celery_app import celery_app
from app.models.dtos.notifications import NotificationCreateDTO
from app.models.enums import NotificationType, ScheduleActionType
import logging
import asyncio
from app.core.db_context import async_session_maker
from app.repos.devices import DeviceRepository
from app.repos.esp_devices import EspDeviceRepository
from app.repos.users import UserRepository
from app.services.devices import DeviceService
from app.models.enums import DeviceType, ControlActionType
from app.exceptions.scheme import AppException
from app.controllers.push.push_notification import PushNotificationController

logger = logging.getLogger(__name__)

_ACTION_MAP = {
    ScheduleActionType.WATER_ON: (
        DeviceType.WATERER,
        ControlActionType.WATER_ON,
    ),
    ScheduleActionType.WATER_OFF: (
        DeviceType.WATERER,
        ControlActionType.WATER_OFF,
    ),
    ScheduleActionType.ATOMIZE_ON: (
        DeviceType.ATOMIZER,
        ControlActionType.ATOMIZE_ON,
    ),
    ScheduleActionType.ATOMIZE_OFF: (
        DeviceType.ATOMIZER,
        ControlActionType.ATOMIZE_OFF,
    ),
    ScheduleActionType.FAN_ON: (
        DeviceType.FANNER,
        ControlActionType.FAN_ON,
    ),
    ScheduleActionType.FAN_OFF: (
        DeviceType.FANNER,
        ControlActionType.FAN_OFF,
    ),
    ScheduleActionType.HEATING_MAT_ON: (
        DeviceType.HEATER,
        ControlActionType.HEATING_MAT_ON,
    ),
    ScheduleActionType.HEATING_MAT_OFF: (
        DeviceType.HEATER,
        ControlActionType.HEATING_MAT_OFF,
    ),
}


@celery_app.task(name="app.schedulers.tasks.run_scheduled_action")
def run_scheduled_action(garden_id: int, action: ScheduleActionType):
    async def inner():
        async with async_session_maker() as db:
            try:
                dev_service = DeviceService(DeviceRepository(db))
                esp_repo = EspDeviceRepository(db)

                if action not in _ACTION_MAP:
                    logger.warning(f"No handler for action: {action}")
                    return

                await dev_service.control_device(await esp_repo.get_by_garden_id(garden_id), *_ACTION_MAP[action])
                logger.info(
                    f"[Scheduled] Executed {action} on garden {garden_id}")

                user_repo = UserRepository(db)
                dto = NotificationCreateDTO(
                    user_id=(await user_repo.get_by_garden_id(garden_id)).id, message=f"Action {action} is executed", type=NotificationType.alert)
                await PushNotificationController.send(dto)

            except AppException as e:
                logger.error(f"[Scheduled] AppException: {e.message}")
            except Exception as e:
                logger.exception(f"[Scheduled] Unexpected error: {e}")

    asyncio.run(inner())


@celery_app.task(name="app.schedulers.tasks.trigger_agent")
def run_trigger_agent(garden_id: int):
    async def inner():
        async with async_session_maker() as db:
            try:
                logger.info("Agent is triggered")
                # TODO take schudelrs and send to agent with its token

            except AppException as e:
                logger.error(f"[Scheduled] AppException: {e.message}")
            except Exception as e:
                logger.exception(f"[Scheduled] Unexpected error: {e}")

    asyncio.run(inner())


@celery_app.task(name="app.schedulers.tasks.demo_log")
def demo_log():
    logger.info("DEMO_LOG: Cyclic test task is running!")
