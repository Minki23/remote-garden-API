import json
import logging
from aiomqtt import Client
from core.mqtt.tls_context import create_tls_context
from core.config import CONFIG

logger = logging.getLogger(__name__)


class MqttTopicPublisher:
    """
    Wrapper for publishing MQTT messages with TLS encryption.
    Uses aiomqtt for async context-based connections.
    """

    def __init__(self):
        """
        Initialize MQTT publisher with broker configuration
        loaded from application CONFIG.
        """
        self.broker_host = CONFIG.MQTT_BROKER_HOST
        self.port = CONFIG.MQTT_BROKER_PORT
        self.tls_context = create_tls_context()

    async def publish(
        self,
        topic: str,
        payload: dict,
        qos: int = 0,
        retain: bool = False,
    ):
        """
        Publish a JSON payload to a given MQTT topic.

        Parameters
        ----------
        topic : str
            MQTT topic to publish to.
        payload : dict
            Message content, automatically serialized to JSON.
        qos : int
            Quality of Service level (0, 1, or 2). Default: 0.
        retain : bool
            Whether the broker should retain this message. Default: False.
        """
        payload_str = json.dumps(payload)

        async with Client(
            self.broker_host,
            port=self.port,
            tls_context=self.tls_context,
        ) as client:
            await client.publish(topic, payload_str.encode(), qos=qos, retain=retain)
            logger.info(f"[MQTT OUT] {topic}: {payload_str}")
