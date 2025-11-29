import json
from datetime import datetime, timezone, timedelta
import logging
from openai import OpenAI
from croniter import croniter

from agent_models.enums import (
    DeviceType,
    ScheduleActionType
)
from agent_clients.backend_agent import BackendAgentClient


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

    openai_api_key = ("key")

    def __init__(self, api_key: str, backend_url: str, garden_id: int, backend_token: str):
        self.client = OpenAI(api_key=api_key)
        self.backend = BackendAgentClient(
            garden_id=garden_id,
            access_token=backend_token,
            base_url=backend_url
        )

    # ------------------------------------------------------------------
    #  COMPUTE STATE FROM JSON WITH CRON OBJECTS
    # ------------------------------------------------------------------

    async def compute_current_state(self):
        """
        Computes device state based on active *_ON schedules.
        Uses croniter to compute next execution for each schedule.
        """
        schedules = await self.backend.list_schedules()
        now = datetime.now(timezone.utc)

        state = {"fan": False, "heater": False,
                 "water": False, "atomizer": False}
        remaining = {"fan": 0, "heater": 0, "water": 0, "atomizer": 0}

        for sch in schedules:

            # IGNORE DISABLED SCHEDULES
            if not sch.enabled:
                continue

            # IGNORE AGENT TASKS (no action)
            if sch.action is None:
                continue

            # Convert cron object → cron string
            cron_obj = sch.cron
            cron_str = f"{cron_obj.minute} {cron_obj.hour} {cron_obj.day_of_month} {cron_obj.month_of_year} {cron_obj.day_of_week}"

            try:
                it = croniter(cron_str, now)
                next_run = it.get_next(datetime)
            except Exception:
                continue

            action = sch.action

            if action == ScheduleActionType.FAN_ON:
                state["fan"] = True
                remaining["fan"] = max(
                    0, int((next_run - now).total_seconds()))

            if action == ScheduleActionType.HEATING_MAT_ON:
                state["heater"] = True
                remaining["heater"] = max(
                    0, int((next_run - now).total_seconds()))

            if action == ScheduleActionType.WATER_ON:
                state["water"] = True
                remaining["water"] = max(
                    0, int((next_run - now).total_seconds()))

            if action == ScheduleActionType.ATOMIZE_ON:
                state["atomizer"] = True
                remaining["atomizer"] = max(
                    0, int((next_run - now).total_seconds()))

        return state, remaining

    # ------------------------------------------------------------------
    #  MAIN ACTION
    # ------------------------------------------------------------------

    async def action(self, plant_name: str):

        plant = plant_name.strip().lower()

        # pobranie odczytów
        temp = await self.backend.get_last_reading(DeviceType.AIR_TEMPERATURE_SENSOR)
        hum = await self.backend.get_last_reading(DeviceType.AIR_HUMIDITY_SENSOR)
        light = await self.backend.get_last_reading(DeviceType.LIGHT_SENSOR)

        sensor_data = {
            "temperature": temp.value,
            "humidity": hum.value,
            "light": light.value
        }

        # Aktualny stan
        state, remaining = await self.compute_current_state()

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
                    {"role": "system",
                        "content": "Return ONLY valid JSON. No explanations."},
                    {"role": "user", "content": prompt}
                ]
            )
            ai = json.loads(completion.choices[0].message.content)
        except Exception:
            ai = {"actions": [], "duration": {}, "reason": "Invalid JSON"}

        actions = ai.get("actions", [])
        durations = ai.get("duration", {})

        executed = []

        # ------------------------------------------------------------------
        # Execute ON/OFF actions
        # ------------------------------------------------------------------
        for act in actions:

            if act not in AI_MAP:
                executed.append(f"Unknown action: {act}")
                continue

            device_type, schedule_action = AI_MAP[act]

            # ON actions
            if act.endswith("_ON"):

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

                run_dt = datetime.now(timezone.utc) + timedelta(seconds=dur)
                cron = f"{run_dt.minute} {run_dt.hour} {run_dt.day} {run_dt.month} *"

                task_id = await self.backend.create_schedule(cron, schedule_action)
                executed.append(
                    f"{act} (duration {dur}s) → schedule {task_id}")

            else:
                # OFF actions – run immediately
                cron = "* * * * *"
                task_id = await self.backend.create_schedule(cron, schedule_action)
                executed.append(f"{act} → schedule {task_id}")

        # ------------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------------

        logging.info("\n=== AGENT REPORT ===")
        logging.info("Sensors:", sensor_data)
        logging.info("State:", state)
        logging.info("Remaining:", remaining)
        logging.info("AI actions:", actions)
        logging.info("AI duration:", durations)
        logging.info("Executed:")
        for e in executed:
            logging.info("-", e)

        return executed
