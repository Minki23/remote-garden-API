from app.core.celery.celery_app import celery_app
from app.models.enums import ScheduleActionType
import logging
import asyncio
from app.core.db_context import async_session_maker
from app.repos.devices import DeviceRepository
from app.services.devices import DeviceService
from app.models.enums import DeviceType, ControlActionType
from app.exceptions.scheme import AppException


logger = logging.getLogger(__name__)

_ACTION_MAP = {
    ScheduleActionType.START_WATERING: (DeviceType.WATER_PUMP, ControlActionType.START_WATERING),
    ScheduleActionType.OPEN_ROOF: (DeviceType.ROOF, ControlActionType.OPEN_ROOF),
    ScheduleActionType.CLOSE_ROOF: (DeviceType.ROOF, ControlActionType.CLOSE_ROOF),
    ScheduleActionType.TURN_ON: (DeviceType.LIGHT, ControlActionType.TURN_ON),
    ScheduleActionType.TURN_OFF: (DeviceType.LIGHT, ControlActionType.TURN_OFF),
    ScheduleActionType.INCREASE_TEMPERATURE: (DeviceType.HEATER, ControlActionType.INCREASE_TEMPERATURE),
    ScheduleActionType.DECREASE_TEMPERATURE: (DeviceType.HEATER, ControlActionType.DECREASE_TEMPERATURE),
}


@celery_app.task(name="app.schedulers.tasks.run_scheduled_action")
def run_scheduled_action(garden_id: int, action: ScheduleActionType):
    async def inner():
        async with async_session_maker() as db:
            try:
                service = DeviceService(DeviceRepository(db))

                if action not in _ACTION_MAP:
                    logger.warning(f"No handler for action: {action}")
                    return

                await service.control_device(garden_id, *_ACTION_MAP[action])
                logger.info(f"[Scheduled] Executed {action} on garden {garden_id}")

            except AppException as e:
                logger.error(f"[Scheduled] AppException: {e.message}")
            except Exception as e:
                logger.exception(f"[Scheduled] Unexpected error: {e}")

    asyncio.run(inner())


@celery_app.task(name="app.schedulers.tasks.demo_log")
def demo_log():
    logger.info("DEMO_LOG: Cyclic test task is running!")
