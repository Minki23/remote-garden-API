from enum import Enum


class DeviceType(str, Enum):
    SOIL_SENSOR = "SOIL_SENSOR"
    LIGHT = "LIGHT"
    TEMPERATURE = "TEMPERATURE"
    CO2 = "CO2"
    ROOF = "ROOF"
    WATER_PUMP = "WATER_PUMP"
    HEATER = "HEATER"
    OTHER = "OTHER"
    ESP = "ESP"


class NotificationType(str, Enum):
    alert = "alert"
    reminder = "reminder"
    system = "system"


class ScheduleActionType(str, Enum):
    TURN_ON = "TURN_ON"
    TURN_OFF = "TURN_OFF"
    START_WATERING = "START_WATERING"
    OPEN_ROOF = "OPEN_ROOF"
    CLOSE_ROOF = "CLOSE_ROOF"
    INCREASE_TEMPERATURE = "INCREASE_TEMPERATURE"
    DECREASE_TEMPERATURE = "DECREASE_TEMPERATURE"


class ControlActionType(str, Enum):
    TURN_ON = "TURN_ON"
    TURN_OFF = "TURN_OFF"
    START_WATERING = "START_WATERING"
    OPEN_ROOF = "OPEN_ROOF"
    CLOSE_ROOF = "CLOSE_ROOF"
    INCREASE_TEMPERATURE = "INCREASE_TEMPERATURE"
    DECREASE_TEMPERATURE = "DECREASE_TEMPERATURE"
    RESET_ESP = "RESET_ESP"
    # PAIR_ESP = "PAIR_ESP"
