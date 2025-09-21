import logging
from app.core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler
from app.core.db_context import async_session_maker
from app.repos.devices import DeviceRepository
from app.repos.users import UserRepository
from app.repos.agents import AgentRepository
from app.core.websocket.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class BaseDeviceHandler(BaseMqttCallbackHandler):
    def __init__(self, topic_template: str):
        super().__init__(topic_template)

    async def process_device_event(
        self,
        topic: str,
        mac: str,
        device_type,
        payload: dict,
        websocket_event: str,
        extra_fields: dict,
    ):
        async with async_session_maker() as session:
            device_repo = DeviceRepository(session)
            device = await device_repo.get_device_by_type_for_esp_mac(mac, device_type)
            if not device:
                logger.warning(
                    f"No {device_type.name} device found for esp with mac {mac}"
                )
                return None, None

            esp = device.esp
            garden_id = esp.garden_id
            user = esp.user
            if not user:
                logger.warning(f"User not found for esp with mac {mac}")
                return device, None

            event_data = {
                "event": websocket_event,
                "device_type": device_type.value,
                "esp_mac": mac,
                "garden_id": garden_id,
                "device_id": device.id,
                **extra_fields,
            }
            await websocket_manager.send_to_user(user.id, event_data)

            logger.info(f"WebSocket {websocket_event} sent to user {user.id}")

            agent_repo = AgentRepository(session)
            agent = await agent_repo.get_by_garden(garden_id)

            if agent:
                await websocket_manager.send_to_agent(agent.id, event_data)

            return device, user
