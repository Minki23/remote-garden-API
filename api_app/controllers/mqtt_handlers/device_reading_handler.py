import logging
import redis
from api_app.controllers.push.push_notification import PushNotificationController
from api_app.models.dtos.notifications import NotificationCreateDTO
from controllers.mqtt_handlers.base_device_handler import BaseDeviceHandler
from core.db_context import async_session_maker
from core.config import CONFIG
from services.readings import ReadingService
from repos.readings import ReadingRepository
from common_db.enums import DeviceType, NotificationType
from models.dtos.readings import ReadingCreateDTO

logger = logging.getLogger(__name__)

# Rate limiting configuration (in seconds)
WATER_LEVEL_NOTIFICATION_COOLDOWN = 3600  # 1 hour

SENSOR_STR_TO_DEVICE_TYPE = {
    "light": DeviceType.LIGHT_SENSOR,
    "air_humidity": DeviceType.AIR_HUMIDITY_SENSOR,
    "soil_moisture": DeviceType.SOIL_MOISTURE_SENSOR,
    "air_temperature": DeviceType.AIR_TEMPERATURE_SENSOR,
    "signal_strenght": DeviceType.SIGNAL_STRENGHT,
    "water_level": DeviceType.WATER_LEVEL,
    "camera": DeviceType.CAMERA
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
        self.redis_client = redis.StrictRedis(
            host=CONFIG.REDIS_HOST,
            port=int(CONFIG.REDIS_PORT),
            decode_responses=True
        )

    def _should_send_water_notification(self, device_id: int) -> bool:
        """
        Check if we should send a water level notification for this device.
        
        Uses Redis to track when the last notification was sent.
        Returns True if enough time has passed since the last notification.
        
        Parameters
        ----------
        device_id : int
            The device ID to check.
            
        Returns
        -------
        bool
            True if notification should be sent, False otherwise.
        """
        key = f"water_level_notif:{device_id}"
        
        # Try to set the key with expiration if it doesn't exist
        # NX means only set if not exists, EX sets expiration time
        result = self.redis_client.set(
            key,
            "1",
            ex=WATER_LEVEL_NOTIFICATION_COOLDOWN,
            nx=True
        )
        
        # If result is True, key was set (didn't exist before) -> send notification
        # If result is None, key already exists -> don't send notification
        return result is not None

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

        device, user = await self.process_device_event(
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

                if device_type == DeviceType.WATER_LEVEL and value < 0.25:
                    # Check if we should send notification (rate limiting)
                    if self._should_send_water_notification(device.id):
                        message = f"Low water level ({value:.2f})."
                        logger.info(f"[ALERT] {message}")

                        notif_dto = NotificationCreateDTO(
                            user_id=user.id,
                            message=message,
                            type=NotificationType.alert,
                        )
                        await PushNotificationController.send(notif_dto)
                    else:
                        logger.debug(
                            f"[ALERT] Skipping water level notification for device {device.id} "
                            f"due to cooldown period"
                        )
