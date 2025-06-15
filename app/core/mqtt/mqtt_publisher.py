import json
import logging
from aiomqtt import Client

logger = logging.getLogger(__name__)

# TODO in future migrate to aiomtt 1.3 and use client.connect() and client.disconnect() methods
class MqttTopicPublisher:
    def __init__(self, broker_host: str = "mqtt-broker", port: int = 1883):
        self.broker_host = broker_host
        self.port = port

    async def publish(self, topic: str, payload: dict, qos: int = 0, retain: bool = False):
        payload_str = json.dumps(payload)

        async with Client(self.broker_host, port=self.port) as client:
            await client.publish(topic, payload_str.encode(), qos=qos, retain=retain)
            logger.info(f"[MQTT OUT] {topic}: {payload_str}")
