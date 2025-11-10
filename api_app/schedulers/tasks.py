import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from clients.agent_client import AgentClient
from core.celery.celery_app import celery_app
from models.dtos.notifications import NotificationCreateDTO
from common_db.enums import NotificationType, ScheduleActionType, DeviceType, ControlActionType
from core.config import CONFIG
from repos.agents import AgentRepository
from repos.devices import DeviceRepository
from repos.esp_devices import EspDeviceRepository
from repos.users import UserRepository
from services.devices import DeviceService
from exceptions.scheme import AppException
from controllers.push.push_notification import PushNotificationController

logger = logging.getLogger(__name__)

DB_URL = CONFIG.DB_CONNECTION_STRING

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


def create_local_session():
    engine = create_async_engine(
        DB_URL, echo=False, pool_size=5, max_overflow=10)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return session_maker, engine


@celery_app.task(name="schedulers.tasks.run_scheduled_action")
def run_scheduled_action(garden_id: int, action: ScheduleActionType):
    async def inner():
        session_maker, engine = create_local_session()
        async with session_maker() as db:
            try:
                if action not in _ACTION_MAP:
                    logger.warning(
                        f"[Scheduled] No handler for action: {action}")
                    return

                device_type, control_action = _ACTION_MAP[action]

                dev_service = DeviceService(DeviceRepository(db))
                esp_repo = EspDeviceRepository(db)

                esp_device = await esp_repo.get_by_garden_id(garden_id)
                await dev_service.control_device(esp_device, device_type, control_action)
                logger.info(
                    f"[Scheduled] Executed {action.name} on garden {garden_id}")

                user_repo = UserRepository(db)
                user = await user_repo.get_by_garden_id(garden_id)

                dto = NotificationCreateDTO(
                    user_id=user.id,
                    message=f"Action {action.name} executed successfully",
                    type=NotificationType.alert,
                )
                await PushNotificationController.send(dto)

            except AppException as e:
                logger.error(f"[Scheduled] AppException: {e.message}")
            except Exception as e:
                logger.exception(f"[Scheduled] Unexpected error: {e}")
            finally:
                await engine.dispose()

    asyncio.run(inner())


@celery_app.task(name="schedulers.tasks.trigger_agent")
def run_trigger_agent(garden_id: int):
    async def inner():
        session_maker, engine = create_local_session()
        async with session_maker() as db:
            try:
                client = AgentClient()
                logger.info(
                    f"[Scheduled] Triggering agent for garden {garden_id}")

                repo = AgentRepository(db)
                agent = await repo.get_by_garden(garden_id)

                if not agent:
                    logger.warning(
                        f"[Scheduled] No agent for garden {garden_id}")
                    return

                await client.trigger(agent.refresh_token_hash, garden_id, agent.context or {})
                logger.info(
                    f"[Scheduled] Agent {agent.id} triggered successfully")

            except AppException as e:
                logger.error(f"[Scheduled] AppException: {e.message}")
            except Exception as e:
                logger.exception(f"[Scheduled] Unexpected error: {e}")
            finally:
                await engine.dispose()

    asyncio.run(inner())
