import json
import asyncio
import time
import os
from openai import OpenAI

# ================================
#   MOCK backend – działa lokalnie
# ================================

class DeviceType:
    TEMPERATURE_SENSOR = "temperature"
    HUMIDITY_SENSOR = "humidity"
    LIGHT_SENSOR = "light"

    FANNER = "fan"
    HEATER = "heater"
    WATERER = "water"
    ATOMIZER = "atomizer"


class ControlActionType:
    FAN_ON = "FAN_ON"
    FAN_OFF = "FAN_OFF"
    HEATING_MAT_ON = "HEATING_MAT_ON"
    HEATING_MAT_OFF = "HEATING_MAT_OFF"
    WATER_ON = "WATER_ON"
    WATER_OFF = "WATER_OFF"
    ATOMIZE_ON = "ATOMIZE_ON"
    ATOMIZE_OFF = "ATOMIZE_OFF"


class MockSensorReading:
    def __init__(self, value):
        self.value = value


class MockBackend:
    """Fake backend with static values."""
    async def get_last_reading(self, device_type):
        example_values = {
            DeviceType.TEMPERATURE_SENSOR: 25,
            DeviceType.HUMIDITY_SENSOR: 55,
            DeviceType.LIGHT_SENSOR: 5
        }
        return MockSensorReading(example_values[device_type])

    async def control_device(self, device, action):
        return f"Mock: wykonano {action} na urządzeniu {device}"


# ================================
#        AgentService
# ================================

DEVICE_STATE_FILE = "device_state.json"
SCHEDULE_FILE = "schedule.json"


class AgentService:
    def __init__(self, openai_api_key: str):
        self.backend_client = MockBackend()
        self.client = OpenAI(api_key=openai_api_key)

        # Wczytaj stan urządzeń
        self.state = self.load_json(DEVICE_STATE_FILE, {
            "fan": False,
            "heater": False,
            "water": False,
            "atomizer": False,
        })

        # Wczytaj harmonogram wyłączeń (UNIX timestamps)
        self.schedule = self.load_json(SCHEDULE_FILE, {
            "fan": 0,
            "heater": 0,
            "water": 0,
            "atomizer": 0,
        })

    # ---------- pomocnicze ----------

    def load_json(self, path, default):
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except:
                pass
        return default

    def save_state(self):
        with open(DEVICE_STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def save_schedule(self):
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(self.schedule, f, indent=2)

    # ---------------------------------

    async def action(self, context: str):

        plant_name = context.strip().lower()
        now = time.time()

        # ---------- Auto-Wyłączenia ----------

        auto_actions = []

        for dev, end_timestamp in self.schedule.items():
            if self.state[dev] and now >= end_timestamp and end_timestamp != 0:
                # czas minął → wyłącz
                off_action = {
                    "fan": "FAN_OFF",
                    "heater": "HEATING_MAT_OFF",
                    "water": "WATER_OFF",
                    "atomizer": "ATOMIZE_OFF"
                }[dev]

                await self.backend_client.control_device(dev, off_action)
                self.state[dev] = False
                self.schedule[dev] = 0
                auto_actions.append(off_action)

        # zapisz zmiany
        self.save_state()
        self.save_schedule()

        # ---------- Pobierz czujniki ----------
        try:
            temp = await self.backend_client.get_last_reading(DeviceType.TEMPERATURE_SENSOR)
            humidity = await self.backend_client.get_last_reading(DeviceType.HUMIDITY_SENSOR)
            light = await self.backend_client.get_last_reading(DeviceType.LIGHT_SENSOR)
        except Exception as e:
            print("Błąd czujników:", e)
            return

        sensor_data = {
            "temperature": temp.value,
            "humidity": humidity.value,
            "light": light.value,
        }

        # ---------- Prompt ----------

        prompt = f"""
You are an expert greenhouse controller.

PLANT: {plant_name}

CURRENT DEVICE STATES:
- fan: {"ON" if self.state["fan"] else "OFF"} (remaining: {max(0, self.schedule["fan"] - now):.0f}s)
- heater: {"ON" if self.state["heater"] else "OFF"} (remaining: {max(0, self.schedule["heater"] - now):.0f}s)
- water: {"ON" if self.state["water"] else "OFF"} (remaining: {max(0, self.schedule["water"] - now):.0f}s)
- atomizer: {"ON" if self.state["atomizer"] else "OFF"} (remaining: {max(0, self.schedule["atomizer"] - now):.0f}s)

SENSOR DATA:
- temperature: {sensor_data['temperature']}
- humidity: {sensor_data['humidity']}
- light: {sensor_data['light']}

TASK:
You must:
1. Decide which devices to turn ON or OFF.
2. For every ON action, provide a duration in SECONDS.
3. Do NOT restart a device that is already ON.
4. If conditions are optimal, return actions to turn OFF all devices that are ON.

Allowed action names (use EXACTLY these strings, no others):
- FAN_ON
- FAN_OFF
- HEATING_MAT_ON
- HEATING_MAT_OFF
- WATER_ON
- WATER_OFF
- ATOMIZE_ON
- ATOMIZE_OFF

FORMAT — ONLY VALID JSON:

{{
  "actions": ["FAN_ON", "HEATING_MAT_OFF", ...],
  "duration": {{
      "fan": 0,
      "heater": 0,
      "water": 0,
      "atomizer": 0
  }},
  "reason": "..."
}}

Example when turning on heater for 300 seconds:

{{
  "actions": ["HEATING_MAT_ON"],
  "duration": {{
      "heater": 300
  }},
  "reason": "Temperature too low"
}}
"""


        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Return ONLY raw JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
            )

            reply = response.choices[0].message.content.strip()
            ai_decision = json.loads(reply)

        except Exception as e:
            print("Błąd AI:", e)
            ai_decision = {"actions": ["NONE"], "duration": {}, "reason": "Error"}


        actions = ai_decision.get("actions", [])
        durations = ai_decision.get("duration", {})
        reason = ai_decision.get("reason", "")

        executed = auto_actions.copy()

        for act in actions:
            if act == "NONE":
                continue

            device_map = {
                "FAN_ON": "fan",
                "FAN_OFF": "fan",
                "HEATING_MAT_ON": "heater",
                "HEATING_MAT_OFF": "heater",
                "WATER_ON": "water",
                "WATER_OFF": "water",
                "ATOMIZE_ON": "atomizer",
                "ATOMIZE_OFF": "atomizer",
            }

            dev = device_map[act]

            # wykonanie akcji
            out = await self.backend_client.control_device(dev, act)
            executed.append(f"{act}: {out}")

            # ustaw stan
            if act.endswith("_ON"):
                self.state[dev] = True

                # zapisz harmonogram
                dur = durations.get(dev, 0)
                self.schedule[dev] = now + dur if dur > 0 else 0

            else:
                self.state[dev] = False
                self.schedule[dev] = 0

        # zapisz stan i schedule
        self.save_state()
        self.save_schedule()

        

        print("\n=== RAPORT AGENDA ===")
        print("Roślina:", plant_name)
        print("Czujniki:", sensor_data)
        print("Stan:", self.state)
        print("Schedule:", self.schedule)
        print("Decyzja AI:", actions)
        print("Powód:", reason)
        print("Wykonane:")
        for e in executed:
            print("-", e)

        return executed




# ================================
#    URUCHOMIENIE TESTOWE
# ================================
async def main():
    agent = AgentService(openai_api_key="apikey")
    await agent.action("dynia")  # <-- tutaj wpisujesz roślinę

asyncio.run(main())
