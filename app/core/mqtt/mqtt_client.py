import asyncio
from aiomqtt import Client
import logging

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(levelname)s:%(name)s:%(message)s"
# )

logger = logging.getLogger(__name__)

async def mqtt_listener():
    logger.info("Connecting to MQTT broker...")
    try:
        async with Client("mqtt-broker", port=1883) as client:
            logger.info("Connected to MQTT broker, subscribing to topic...")
            await client.subscribe("device/1/status")

            async for message in client.messages:
                logger.info(f"[MQTT IN] {message.topic}: {message.payload.decode()}")
    except Exception as e:
        logger.exception("MQTT listener failed")