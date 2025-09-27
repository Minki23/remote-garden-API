import logging
from core.db_context import async_session_maker
from core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler
from repos.esp_devices import EspDeviceRepository

logger = logging.getLogger(__name__)


class StatusHandler(BaseMqttCallbackHandler):
    """
    Handles incoming MQTT status messages from ESP devices.

    Listens on the topic ``{mac}/status``. Updates the online/offline
    status of the ESP device in the database.
    """

    def __init__(self):
        """
        Initialize the status handler with the topic template.
        """
        super().__init__("{mac}/status")

    async def __call__(self, topic: str, payload: dict):
        """
        Process a status message from an ESP device.

        Parameters
        ----------
        topic : str
            The MQTT topic containing the device MAC.
        payload : dict
            JSON payload containing:
            - online : bool
                Whether the device is currently online.

        Notes
        -----
        - Extracts the device MAC from the topic.
        - Updates the corresponding ESP device status in the database.
        - Logs warnings if the MAC cannot be extracted or the device is missing.
        """
        logger.info(f"[STATUS] topic={topic}, payload={payload}")

        status = payload.get("online")
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
