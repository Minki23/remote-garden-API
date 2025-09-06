import logging
from app.controllers.mqtt_handlers.base_device_handler import BaseDeviceHandler
from app.core.db_context import async_session_maker
from app.services.readings import ReadingService
from app.repos.readings import ReadingRepository
from app.models.enums import DeviceType
from app.models.dtos.readings import ReadingCreateDTO

logger = logging.getLogger(__name__)

SENSOR_STR_TO_DEVICE_TYPE = {
    "light": DeviceType.LIGHT_SENSOR,
    "air_humidity": DeviceType.AIR_HUMIDITY_SENSOR,
    "soil_moisture": DeviceType.SOIL_MOISTURE_SENSOR,
    "air_temperature": DeviceType.AIR_TEMPERATURE_SENSOR,
    "signal_strenght": DeviceType.SIGNAL_STRENGHT,
    "battery": DeviceType.BATTERY
}


class DeviceReadingHandler(BaseDeviceHandler):
    def __init__(self):
        super().__init__("{mac}/device/sensor")

    async def __call__(self, topic: str, payload: dict):
        logger.info(f"[SENSOR] topic={topic}, payload={payload}")

        sensor_str = payload.get("sensor")
        if sensor_str not in SENSOR_STR_TO_DEVICE_TYPE:
            logger.warning(f"Unknown sensor type '{sensor_str}' in payload.")
            return
        device_type = SENSOR_STR_TO_DEVICE_TYPE[sensor_str]

        values = payload.get("values")
        if values is None:
            logger.warning(f"Missing 'value' in {device_type.name} payload.")
            return

        try:
            mac = self.extract_from_topic(topic, "mac")
        except (ValueError, TypeError):
            logger.warning(f"Could not extract valid mac from topic: {topic}")
            return

        device, _ = await self.process_device_event(
            topic,
            mac,
            device_type,
            payload,
            websocket_event="new_reading",
            extra_fields={"values": values},
        )

        if device:
            async with async_session_maker() as session:
                reading_service = ReadingService(ReadingRepository(session))
                for value in values:
                    dto = ReadingCreateDTO(
                        device_id=device.id, value=str(value))
                    await reading_service.create(dto)
