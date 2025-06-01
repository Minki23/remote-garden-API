import logging
from app.core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler
from app.core.db_context import async_session_maker
from app.core.websocket.websocket_manager import websocket_manager
from app.services.readings import ReadingService
from app.repos.readings import ReadingRepository
from app.repos.devices import DeviceRepository
from app.repos.users import UserRepository
from app.models.enums import DeviceType
from app.models.dtos.readings import ReadingCreateDTO

logger = logging.getLogger(__name__)


class DeviceReadingHandler(BaseMqttCallbackHandler):
    def __init__(self, topic_template: str, device_type: DeviceType):
        super().__init__(topic_template)
        self.device_type = device_type

    async def __call__(self, topic: str, payload: dict):
        logger.info(f"[{self.device_type.name} SENSOR] topic={topic}, payload={payload}")

        value = payload.get("value")
        if value is None:
            logger.warning(f"Missing 'value' in {self.device_type.name} payload.")
            return
        # @TODO change to validation of mac adres, not garden id - more flexible in future
        try:
            garden_id = int(self.extract_from_topic(topic, "garden_id"))
        except (ValueError, TypeError):
            logger.warning(f"Could not extract valid garden_id from topic: {topic}")
            return

        async with async_session_maker() as session:
            device_repo = DeviceRepository(session)
            device = await device_repo.get_by_garden_id_and_type(garden_id, self.device_type)
            if not device:
                logger.warning(f"No {self.device_type.name} device found for garden {garden_id}")
                return

            reading_service = ReadingService(ReadingRepository(session))
            dto = ReadingCreateDTO(device_id=device.id, value=str(value))
            await reading_service.create(dto)
            logger.info(f"Saved {self.device_type.name} reading for device {device.id} in garden {garden_id}")

            try:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_garden_id(garden_id)
                if not user:
                    logger.warning(f"User not found for garden {garden_id}")
                    return

                await websocket_manager.send_to_user(user.id, {
                    "event": "new_reading",
                    "device_type": self.device_type.value,
                    "value": value,
                    "garden_id": garden_id,
                    "device_id": device.id
                })
                logger.info(f"WebSocket event sent to user {user.id}")
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
