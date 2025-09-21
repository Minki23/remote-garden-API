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
