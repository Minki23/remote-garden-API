import json
from datetime import datetime, timezone, timedelta
from openai import OpenAI

from agent_models.enums import (
    DeviceType,
    ControlActionType,
    ScheduleActionType
)
from agent_app.agent_clients.backend_agent import BackendAgentClient


AI_MAP = {
    "FAN_ON": (DeviceType.FANNER, ScheduleActionType.FAN_ON),
    "FAN_OFF": (DeviceType.FANNER, ScheduleActionType.FAN_OFF),

    "HEATING_MAT_ON": (DeviceType.HEATER, ScheduleActionType.HEATING_MAT_ON),
    "HEATING_MAT_OFF": (DeviceType.HEATER, ScheduleActionType.HEATING_MAT_OFF),

    "WATER_ON": (DeviceType.WATERER, ScheduleActionType.WATER_ON),
    "WATER_OFF": (DeviceType.WATERER, ScheduleActionType.WATER_OFF),

    "ATOMIZE_ON": (DeviceType.ATOMIZER, ScheduleActionType.ATOMIZE_ON),
    "ATOMIZE_OFF": (DeviceType.ATOMIZER, ScheduleActionType.ATOMIZE_OFF),
}


class AgentService:

    openai_api_key=("key")

    def __init__(self, api_key: str, garden_id: int, backend_token: str):
        self.client = OpenAI(api_key=api_key)
        self.backend = BackendAgentClient(garden_id=garden_id, access_token=backend_token)

    async def compute_current_state(self):
        """
        Stan urządzeń wynika z aktywnych schedule typu *_ON.
        Zwraca:
        state = {"fan": bool, ...}
        remaining = {"fan": sec_remaining, ...}
        """
        schedules = await self.backend.list_schedules()
        now = datetime.now(timezone.utc)

        state = {"fan": False, "heater": False, "water": False, "atomizer": False}
        remaining = {"fan": 0, "heater": 0, "water": 0, "atomizer": 0}

        for sch in schedules:
            action = sch.action
            run_time = sch.cron_next_run  # backend zwraca next run datetime

            # ON schedules
            if action == ScheduleActionType.FAN_ON:
                state["fan"] = True
                remaining["fan"] = max(0, int((run_time - now).total_seconds()))

            if action == ScheduleActionType.HEATING_MAT_ON:
                state["heater"] = True
                remaining["heater"] = max(0, int((run_time - now).total_seconds()))

            if action == ScheduleActionType.WATER_ON:
                state["water"] = True
                remaining["water"] = max(0, int((run_time - now).total_seconds()))

            if action == ScheduleActionType.ATOMIZE_ON:
                state["atomizer"] = True
                remaining["atomizer"] = max(0, int((run_time - now).total_seconds()))

        return state, remaining


    async def action(self, plant_name: str):

        plant = plant_name.strip().lower()

        # pobranie odczytów
        temp = await self.backend.get_last_reading(DeviceType.TEMPERATURE_SENSOR)
        hum = await self.backend.get_last_reading(DeviceType.HUMIDITY_SENSOR)
        light = await self.backend.get_last_reading(DeviceType.LIGHT_SENSOR)

        sensor_data = {
            "temperature": temp.value,
            "humidity": hum.value,
            "light": light.value
        }

        # pobranie stanu z backendu
        state, remaining = await self.compute_current_state()
        now_ts = datetime.now(timezone.utc).timestamp()

        
        prompt = f"""
You are an expert greenhouse controller.

PLANT: {plant}

CURRENT DEVICE STATES:
- fan: {"ON" if state["fan"] else "OFF"} (remaining: {remaining["fan"]}s)
- heater: {"ON" if state["heater"] else "OFF"} (remaining: {remaining["heater"]}s)
- water: {"ON" if state["water"] else "OFF"} (remaining: {remaining["water"]}s)
- atomizer: {"ON" if state["atomizer"] else "OFF"} (remaining: {remaining["atomizer"]}s)

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
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {"role": "system", "content": "Return ONLY valid JSON. No explanations."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = completion.choices[0].message.content
            ai = json.loads(content)
        except Exception:
            print("AI error or invalid JSON:", completion)
            ai = {"actions": [], "duration": {}, "reason": "Invalid JSON"}

        actions = ai.get("actions", [])
        durations = ai.get("duration", {})

        executed = []

        
        for act in actions:

            if act not in AI_MAP:
                executed.append(f"Unknown action: {act}")
                continue

            device_type, schedule_action = AI_MAP[act]

            # jeśli to akcja ON
            if act.endswith("_ON"):

                # ale urządzenie jest już ON → pomijamy
                dev_key = {
                    DeviceType.FANNER: "fan",
                    DeviceType.HEATER: "heater",
                    DeviceType.WATERER: "water",
                    DeviceType.ATOMIZER: "atomizer"
                }[device_type]

                if state[dev_key] is True:
                    executed.append(f"{act}: skipped (already ON)")
                    continue

                dur = durations.get(dev_key, 0)
                if dur <= 0:
                    executed.append(f"{act}: invalid duration {dur}")
                    continue

                # data wykonania
                run_dt = datetime.now(timezone.utc) + timedelta(seconds=dur)
                cron = f"{run_dt.minute} {run_dt.hour} {run_dt.day} {run_dt.month} *"

                task_id = await self.backend.create_schedule(cron, schedule_action)
                executed.append(f"{act} (duration {dur}s) → schedule {task_id}")

            else:
                # akcje OFF
                cron = "* * * * *"  # wykonaj od razu
                task_id = await self.backend.create_schedule(cron, schedule_action)
                executed.append(f"{act} → schedule {task_id}")

        # Do edycji lub usunięcia

        print("\n=== AGENT REPORT ===")
        print("Sensors:", sensor_data)
        print("State:", state)
        print("Remaining:", remaining)
        print("AI actions:", actions)
        print("AI duration:", durations)
        print("Executed:")
        for e in executed:
            print("-", e)

        return executed
