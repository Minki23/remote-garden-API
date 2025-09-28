from clients.agent_client import AgentClient
from core.celery.celery_app import celery_app
from models.dtos.notifications import NotificationCreateDTO
from common_db.enums import NotificationType, ScheduleActionType
import logging
import asyncio
from core.db_context import async_session_maker
from repos.agents import AgentRepository
from repos.devices import DeviceRepository
from repos.esp_devices import EspDeviceRepository
from repos.users import UserRepository
from services.devices import DeviceService
from common_db.enums import DeviceType, ControlActionType
from exceptions.scheme import AppException
from controllers.push.push_notification import PushNotificationController

logger = logging.getLogger(__name__)

_ACTION_MAP = {
    ScheduleActionType.WATER_ON: (DeviceType.WATERER, ControlActionType.WATER_ON),
    ScheduleActionType.WATER_OFF: (DeviceType.WATERER, ControlActionType.WATER_OFF),
    ScheduleActionType.ATOMIZE_ON: (DeviceType.ATOMIZER, ControlActionType.ATOMIZE_ON),
    ScheduleActionType.ATOMIZE_OFF: (DeviceType.ATOMIZER, ControlActionType.ATOMIZE_OFF),
    ScheduleActionType.FAN_ON: (DeviceType.FANNER, ControlActionType.FAN_ON),
    ScheduleActionType.FAN_OFF: (DeviceType.FANNER, ControlActionType.FAN_OFF),
    ScheduleActionType.HEATING_MAT_ON: (DeviceType.HEATER, ControlActionType.HEATING_MAT_ON),
    ScheduleActionType.HEATING_MAT_OFF: (DeviceType.HEATER, ControlActionType.HEATING_MAT_OFF),
}


@celery_app.task(name="schedulers.tasks.run_scheduled_action")
def run_scheduled_action(garden_id: int, action: ScheduleActionType):
    """
    Execute a scheduled action for a garden.

    Controls the device mapped to the given schedule action
    and notifies the garden owner about the execution.
    """
    async def inner():
        async with async_session_maker() as db:
            try:
                dev_service = DeviceService(DeviceRepository(db))
                esp_repo = EspDeviceRepository(db)

                if action not in _ACTION_MAP:
                    logger.warning(f"No handler for action: {action}")
                    return

                await dev_service.control_device(
                    await esp_repo.get_by_garden_id(garden_id),
                    *_ACTION_MAP[action]
                )
                logger.info(
                    f"[Scheduled] Executed {action} on garden {garden_id}")

                user_repo = UserRepository(db)
                dto = NotificationCreateDTO(
                    user_id=(await user_repo.get_by_garden_id(garden_id)).id,
                    message=f"Action {action} is executed",
                    type=NotificationType.alert,
                )
                await PushNotificationController.send(dto)

            except AppException as e:
                logger.error(f"[Scheduled] AppException: {e.message}")
            except Exception as e:
                logger.exception(f"[Scheduled] Unexpected error: {e}")

    asyncio.run(inner())


@celery_app.task(name="schedulers.tasks.trigger_agent")
def run_trigger_agent(garden_id: int):
    """
    Trigger the agent assigned to a garden.

    Calls the external agent service if an agent is linked
    to the given garden.
    """
    async def inner():
        async with async_session_maker() as db:
            try:
                client = AgentClient()
                logger.info("Agent is triggered")

                repo = AgentRepository(db)
                agent = await repo.get_by_garden(garden_id)

                if agent:
                    await client.trigger(agent.id, garden_id, agent.context)
                else:
                    logger.warning("Cannot trigger agent")

            except AppException as e:
                logger.error(f"[Scheduled] AppException: {e.message}")
            except Exception as e:
                logger.exception(f"[Scheduled] Unexpected error: {e}")

    asyncio.run(inner())
