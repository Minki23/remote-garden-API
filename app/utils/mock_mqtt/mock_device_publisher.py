import asyncio
import json
import random
import logging
from aiomqtt import Client, Message
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-mqtt-publisher")

GARDEN_ID = 1


class ControlActionType(str, Enum):
    TURN_ON = "TURN_ON"
    TURN_OFF = "TURN_OFF"
    START_WATERING = "START_WATERING"
    OPEN_ROOF = "OPEN_ROOF"
    CLOSE_ROOF = "CLOSE_ROOF"
    INCREASE_TEMPERATURE = "INCREASE_TEMPERATURE"
    DECREASE_TEMPERATURE = "DECREASE_TEMPERATURE"
    RESET_ESP = "RESET_ESP"


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


class DeviceState:
    def __init__(self):
        self.light_on = False
        self.roof_open = False
        self.watering_active = False
        self.temperature_offset = 0
        self._lock = asyncio.Lock()

    async def start_watering(self):
        async with self._lock:
            self.watering_active = True
        await asyncio.sleep(20)
        async with self._lock:
            self.watering_active = False


state = DeviceState()


async def publish_mock_data(client: Client):
    while True:
        await client.publish(
            f"device/{GARDEN_ID}/status",
            json.dumps(
                {
                    "mac": MACS["status"],
                    "battery_level": round(random.uniform(40, 100), 2),
                    "signal_strength": random.randint(-80, -50),
                    "is_online": True,
                    "system_ok": random.choice([True, True, False]),
                }
            ),
        )
        logger.info("Published status")

        await client.publish(
            f"device/{GARDEN_ID}/soil",
            json.dumps(
                {"mac": MACS["soil"], "value": round(random.uniform(30, 70), 1)}
            ),
        )
        logger.info("Published soil")

        base_temp = (18 + state.temperature_offset, 20 + state.temperature_offset)
        await client.publish(
            f"device/{GARDEN_ID}/temperature",
            json.dumps(
                {
                    "mac": MACS["temperature"],
                    "value": round(random.uniform(*base_temp), 1),
                }
            ),
        )
        logger.info("Published temperature")

        await client.publish(
            f"device/{GARDEN_ID}/co2",
            json.dumps({"mac": MACS["co2"], "value": random.randint(350, 800)}),
        )
        logger.info("Published co2")

        await client.publish(
            f"device/{GARDEN_ID}/light",
            json.dumps({"mac": MACS["light"], "value": state.light_on}),
        )
        logger.info("Published light")

        await client.publish(
            f"device/{GARDEN_ID}/water",
            json.dumps({"mac": MACS["water_pump"], "value": state.watering_active}),
        )
        logger.info("Published water_pump")

        await client.publish(
            f"device/{GARDEN_ID}/roof",
            json.dumps({"mac": MACS["roof"], "value": state.roof_open}),
        )
        logger.info("Published roof")

        await client.publish(
            f"device/{GARDEN_ID}/heater",
            json.dumps({"mac": MACS["heater"], "value": False}),
        )
        logger.info("Published heater")

        await asyncio.sleep(5)


async def handle_control(payload: dict):
    action = payload.get("action")

    match action:
        case ControlActionType.TURN_ON:
            state.light_on = True
        case ControlActionType.TURN_OFF:
            state.light_on = False
        case ControlActionType.OPEN_ROOF:
            state.roof_open = True
        case ControlActionType.CLOSE_ROOF:
            state.roof_open = False
        case ControlActionType.INCREASE_TEMPERATURE:
            state.temperature_offset += 5
        case ControlActionType.DECREASE_TEMPERATURE:
            state.temperature_offset = max(0, state.temperature_offset - 5)
        case ControlActionType.START_WATERING:
            asyncio.create_task(state.start_watering())
        case ControlActionType.RESET_ESP:
            logger.info("ESP reset requested (no-op in mock).")
        case _:
            logger.warning(f"Unknown action: {action}")


async def handle_configure(payload: dict):
    ssid = payload.get("ssid")
    password = payload.get("password")
    logger.info(f"[CONFIGURE] Received Wi-Fi credentials: SSID={ssid}, PASS={password}")


async def handle_incoming_messages(client: Client):
    await client.subscribe(f"device/{GARDEN_ID}/control")
    await client.subscribe(f"device/{GARDEN_ID}/configure")
    logger.info(f"Subscribed to device/{GARDEN_ID}/control and /configure")

    async for message in client.messages:
        try:
            payload = json.loads(message.payload.decode())
            topic = str(message.topic)
            logger.info(f"[INCOMING] {topic}: {json.dumps(payload)}")

            if topic.endswith("/control"):
                await handle_control(payload)
            elif topic.endswith("/configure"):
                await handle_configure(payload)

        except Exception as e:
            logger.error(f"Error handling message: {e}")


async def main():
    async with Client("mqtt-broker", port=1883) as client:
        logger.info("Connected to MQTT broker")
        await asyncio.gather(
            publish_mock_data(client),
            handle_incoming_messages(client),
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
