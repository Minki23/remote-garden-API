from app.core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler
import logging

logger = logging.getLogger(__name__)


class DeviceStatusHandler(BaseMqttCallbackHandler):
    def __init__(self):
        super().__init__("device/{garden_id}/status")

    async def __call__(self, topic: str, payload: dict):
        logger.info(f"[DEVICE STATUS] topic={topic}, payload={payload}")
