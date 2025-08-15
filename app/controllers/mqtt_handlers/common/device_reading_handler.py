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

SENSOR_STR_TO_DEVICE_TYPE = {
    "light": DeviceType.LIGHT_SENSOR,
    "air_humidity": DeviceType.AIR_HUMIDITY_SENSOR,
    "soil_moisture": DeviceType.SOIL_MOISTURE_SENSOR,
    "air_temperature": DeviceType.AIR_TEMPERATURE_SENSOR,
}
# TODO battery i signal strenght


class DeviceReadingHandler(BaseMqttCallbackHandler):
    def __init__(self):
        super().__init__("{mac}/device/sensor")

    async def __call__(self, topic: str, payload: dict):
        logger.info(
            f"[SENSOR] topic={topic}, payload={payload}"
        )

        sensor_str = payload.get("sensor")
        if sensor_str not in SENSOR_STR_TO_DEVICE_TYPE:
            logger.warning(f"Unknown sensor type '{sensor_str}' in payload.")
            return
        device_type = SENSOR_STR_TO_DEVICE_TYPE[sensor_str]

        value = payload.get("value")
        if value is None:
            logger.warning(
                f"Missing 'value' in {device_type.name} payload.")
            return

        try:
            mac = int(self.extract_from_topic(topic, "mac"))
        except (ValueError, TypeError):
            logger.warning(
                f"Could not extract valid mac from topic: {topic}")
            return

        async with async_session_maker() as session:
            device_repo = DeviceRepository(session)
            device = await device_repo.get_device_by_type_for_esp_mac(
                mac, device_type
            )
            if not device:
                logger.warning(
                    f"No {device_type.name} device found for esp with mac {mac}"
                )
                return

            esp = device.esp
            garden_id = esp.garden_id
            reading_service = ReadingService(ReadingRepository(session))
            dto = ReadingCreateDTO(device_id=device.id, value=str(value))
            await reading_service.create(dto)
            logger.info(
                f"Saved {device_type.name} reading for device {device.id} in esp with mac {mac}"
            )

            try:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_garden_id(garden_id)
                if not user:
                    logger.warning(f"User not found for esp with mac {mac}")
                    return

                await websocket_manager.send_to_user(
                    user.id,
                    {
                        "event": "new_reading",
                        "device_type": device_type.value,
                        "value": value,
                        "esp_mac": mac,
                        "garden_id": garden_id,
                        "device_id": device.id,
                    },
                )
                logger.info(f"WebSocket event sent to user {user.id}")
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
