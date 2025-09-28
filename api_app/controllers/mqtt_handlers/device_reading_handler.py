import logging
from controllers.mqtt_handlers.base_device_handler import BaseDeviceHandler
from core.db_context import async_session_maker
from services.readings import ReadingService
from repos.readings import ReadingRepository
from common_db.enums import DeviceType
from models.dtos.readings import ReadingCreateDTO

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
    """
    Handles incoming MQTT sensor readings from ESP devices.

    Listens on the topic ``{mac}/device/sensor``. Maps sensor string
    identifiers to device types and stores readings into the database.
    Also propagates the data via WebSocket events to connected clients.
    """

    def __init__(self):
        """
        Initialize the reading handler with the topic template.
        """
        super().__init__("{mac}/device/sensor")

    async def __call__(self, topic: str, payload: dict):
        """
        Process a new sensor reading.

        Parameters
        ----------
        topic : str
            The MQTT topic containing the device MAC and sensor data.
        payload : dict
            JSON payload containing:
            - sensor : str
                Type of the sensor (light, soil_moisture, etc.)
            - values : list[float]
                The measurements collected by the sensor.
        """
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
