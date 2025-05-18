import asyncio
import json
import random
import logging
from aiomqtt import Client

# Konfiguracja loggera
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-mqtt-publisher")


async def publish_mock_data():
    async with Client("mqtt-broker", port=1883) as client:
        logger.info("Connected to MQTT broker at mqtt-broker:1883")
        while True:
            payload = {
                "battery_level": round(random.uniform(40, 100), 2),
                "signal_strength": random.randint(-80, -50),
                "is_online": True,
                "system_ok": random.choice([True, True, False]),
            }
            payload_json = json.dumps(payload)
            await client.publish("device/1/status", payload_json)
            logger.info(f"Published to topic 'device/1/status': {payload_json}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(publish_mock_data())
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
