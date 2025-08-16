import logging
from app.core.db_context import async_session_maker
from app.core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler
from app.repos.esp_devices import EspDeviceRepository

logger = logging.getLogger(__name__)


class StatusHandler(BaseMqttCallbackHandler):
    def __init__(self):
        super().__init__("{mac}/status")

    async def __call__(self, topic: str, payload: dict):
        logger.info(f"[STATUS] topic={topic}, payload={payload}")

        status = payload.get("status")
        if status is None:
            logger.warning(f"Missing 'status' in payload: {payload}")
            return

        try:
            mac = self.extract_from_topic(topic, "mac")
        except (ValueError, TypeError):
            logger.warning(f"Could not extract valid mac from topic: {topic}")
            return

        async with async_session_maker() as session:
            esp_repo = EspDeviceRepository(session)
            esp = await esp_repo.get_by_mac(mac)
            if not esp:
                logger.warning(f"No ESP found for mac {mac}")
                return

            await esp_repo.update(esp.id, status=bool(status))
            logger.info(f"ESP {mac} status updated to {status}")
