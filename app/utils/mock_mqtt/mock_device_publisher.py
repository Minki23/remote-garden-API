import asyncio
import json
import random
import logging
from aiomqtt import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-mqtt-publisher")

GARDEN_ID = 1

MACS = {
    "status": "MAC-STAT-001",
    "soil": "MAC-SOIL-001",
    "temperature": "MAC-TEMP-001",
    "co2": "MAC-CO2-001",
    "light": "MAC-LIGHT-001",
    "water_pump": "MAC-PUMP-001",
    "roof": "MAC-ROOF-001",
    "heater": "MAC-HEAT-001",
}


async def publish_mock_data():
    async with Client("mqtt-broker", port=1883) as client:
        logger.info("Connected to MQTT broker at mqtt-broker:1883")
        while True:
            await client.publish(f"device/{GARDEN_ID}/status", json.dumps({
                "mac": MACS["status"],
                "battery_level": round(random.uniform(40, 100), 2),
                "signal_strength": random.randint(-80, -50),
                "is_online": True,
                "system_ok": random.choice([True, True, False]),
            }))
            logger.info("Published status")

            await client.publish(f"device/{GARDEN_ID}/soil", json.dumps({
                "mac": MACS["soil"],
                "value": round(random.uniform(30, 70), 1)
            }))
            logger.info("Published soil")

            await client.publish(f"device/{GARDEN_ID}/temperature", json.dumps({
                "mac": MACS["temperature"],
                "value": round(random.uniform(15, 30), 1)
            }))
            logger.info("Published temperature")

            await client.publish(f"device/{GARDEN_ID}/co2", json.dumps({
                "mac": MACS["co2"],
                "value": random.randint(350, 800)
            }))
            logger.info("Published co2")

            await client.publish(f"device/{GARDEN_ID}/light", json.dumps({
                "mac": MACS["light"],
                "value": round(random.uniform(100, 1000), 1)
            }))
            logger.info("Published light")

            await client.publish(f"device/{GARDEN_ID}/water_pump", json.dumps({
                "mac": MACS["water_pump"],
                "value": random.choice([True, False])
            }))
            logger.info("Published water_pump")

            await client.publish(f"device/{GARDEN_ID}/roof", json.dumps({
                "mac": MACS["roof"],
                "value": random.choice([True, False])
            }))
            logger.info("Published roof")

            await client.publish(f"device/{GARDEN_ID}/heater", json.dumps({
                "mac": MACS["heater"],
                "value": random.choice([True, False])
            }))
            logger.info("Published heater")

            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(publish_mock_data())
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
