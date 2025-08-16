from enum import Enum


class DeviceType(str, Enum):
    LIGHT_SENSOR = "LIGHT_SENSOR"
    AIR_HUMIDITY_SENSOR = "AIR_HUMIDITY_SENSOR"
    SOIL_MOISTURE_SENSOR = "SOIL_MOISTURE_SENSOR"
    AIR_TEMPERATURE_SENSOR = "AIR_TEMPERATURE_SENSOR"
    SIGNAL_STRENGHT = "SIGNAL_STRENGHT"
    BATTERY = "BATTERY"
    WATERER = "WATERER"
    ATOMIZER = "ATOMIZER"
    FANNER = "FANNER"
    HEATER = "HEATER"


class NotificationType(str, Enum):
    alert = "alert"
    reminder = "reminder"
    system = "system"


class ScheduleActionType(str, Enum):
    WATER_ON = "WATER_ON"
    WATER_OFF = "WATER_OFF"
    ATOMIZE_ON = "ATOMIZE_ON"
    ATOMIZE_OFF = "ATOMIZE_OFF"
    FAN_ON = "FAN_ON"
    FAN_OFF = "FAN_OFF"
    HEATING_MAT_ON = "HEATING_MAT_ON"
    HEATING_MAT_OFF = "HEATING_MAT_OFF"


class ControlActionType(str, Enum):
    WATER_ON = "WATER_ON"
    WATER_OFF = "WATER_OFF"
    ATOMIZE_ON = "ATOMIZE_ON"
    ATOMIZE_OFF = "ATOMIZE_OFF"
    FAN_ON = "FAN_ON"
    FAN_OFF = "FAN_OFF"
    HEATING_MAT_ON = "HEATING_MAT_ON"
    HEATING_MAT_OFF = "HEATING_MAT_OFF"
