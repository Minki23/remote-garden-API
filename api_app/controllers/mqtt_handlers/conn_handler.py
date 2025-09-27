import logging
from controllers.push.push_notification import PushNotificationController
from core.db_context import async_session_maker
from core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler
from models.dtos.notifications import NotificationCreateDTO
from repos.esp_devices import EspDeviceRepository
from repos.notifications import NotificationRepository
from repos.users import UserRepository
from services.notifications import NotificationService
from common_db.enums import NotificationType

logger = logging.getLogger(__name__)


class ConnHandler(BaseMqttCallbackHandler):
    """
    Handles MQTT connection events published by ESP devices.

    This handler listens on the ``{mac}/conn`` topic, validates the
    connection payload, and links an ESP device to the appropriate user
    account. It also issues a push notification confirming the binding.
    """

    def __init__(self):
        """
        Initialize the connection handler with the topic template.
        """
        super().__init__("{mac}/conn")

    async def __call__(self, topic: str, payload: dict):
        """
        Process an ESP connection event.

        Parameters
        ----------
        topic : str
            The MQTT topic carrying the event (e.g. ``AA:BB:CC:DD:EE:FF/conn``).
        payload : dict
            JSON payload containing at minimum the user key.
        """
        logger.info(f"[CONN] topic={topic}, payload={payload}")

        user_key = payload.get("userKey")
        if user_key is None:
            logger.warning(f"Missing 'userKey' in {payload}.")
            return

        try:
            mac = self.extract_from_topic(topic, "mac")
        except (ValueError, TypeError):
            logger.warning(f"Could not extract valid mac from topic: {topic}")
            return

        async with async_session_maker() as session:
            esp_repo = EspDeviceRepository(session)
            esp = await esp_repo.get_by_mac(mac)

            user = await UserRepository(session).get_by_user_key(user_key)
            if not user:
                logger.warning(f"No user found for key {user_key}")
                return

            await esp_repo.update(esp.id, user_id=user.id)

            dto = NotificationCreateDTO(
                user_id=user.id,
                message=f"ESP {esp.mac} is connected to your account",
                type=NotificationType.alert,
            )
            await PushNotificationController.send(dto)
