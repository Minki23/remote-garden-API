import logging
from app.core.db_context import async_session_maker
from app.core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler
from app.models.dtos.notifications import NotificationCreateDTO
from app.repos.esp_devices import EspDeviceRepository
from app.repos.notifications import NotificationRepository
from app.repos.users import UserRepository
from app.services.notifications import NotificationService
from app.models.enums import NotificationType

logger = logging.getLogger(__name__)


class ConnHandler(BaseMqttCallbackHandler):
    def __init__(self):
        super().__init__("{mac}/conn")

    async def __call__(self, topic: str, payload: dict):
        logger.info(f"[CONN] topic={topic}, payload={payload}")

        user_key = payload.get("userKey")
        if user_key is None:
            logger.warning(
                f"Missing 'user_key' in {payload}.")
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

            not_service = NotificationService(NotificationRepository(session))
            not_service.create(NotificationCreateDTO(
                user_id=user.id, message=f"ESP {esp.mac} is attached to your account", type=NotificationType.alert))
