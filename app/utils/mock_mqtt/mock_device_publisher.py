import asyncio
import json
import random
import logging
from aiomqtt import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-mqtt-publisher")


async def publish_mock_data():
    async with Client("mqtt-broker", port=1883) as client:
        logger.info("Connected to MQTT broker at mqtt-broker:1883")
        while True:
            status_payload = {
                "battery_level": round(random.uniform(40, 100), 2),
                "signal_strength": random.randint(-80, -50),
                "is_online": True,
                "system_ok": random.choice([True, True, False]),
            }
            soil_payload = {"value": round(random.uniform(30, 70), 1)}
            temperature_payload = {"value": round(random.uniform(15, 30), 1)}
            co2_payload = {"value": random.randint(350, 800)}
            light_payload = {"value": round(random.uniform(100, 1000), 1)}
            water_pump_payload = {"value": random.choice([True, False])}
            roof_payload = {"value": random.choice([True, False])}
            heater_payload = {"value": random.choice([True, False])}

            await client.publish("device/1/status", json.dumps(status_payload))
            logger.info(f"Published to device/1/status: {status_payload}")

            await client.publish("device/1/soil", json.dumps(soil_payload))
            logger.info(f"Published to device/1/soil: {soil_payload}")

            await client.publish("device/1/temperature", json.dumps(temperature_payload))
            logger.info(f"Published to device/1/temperature: {temperature_payload}")

            await client.publish("device/1/co2", json.dumps(co2_payload))
            logger.info(f"Published to device/1/co2: {co2_payload}")

            await client.publish("device/1/light", json.dumps(light_payload))
            logger.info(f"Published to device/1/light: {light_payload}")

            await client.publish("device/1/water_pump", json.dumps(water_pump_payload))
            logger.info(f"Published to device/1/water_pump: {water_pump_payload}")

            await client.publish("device/1/roof", json.dumps(roof_payload))
            logger.info(f"Published to device/1/roof: {roof_payload}")

            await client.publish("device/1/heater", json.dumps(heater_payload))
            logger.info(f"Published to device/1/heater: {heater_payload}")

            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(publish_mock_data())
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
