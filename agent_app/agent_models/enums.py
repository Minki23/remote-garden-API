from enum import Enum, IntEnum


class DeviceType(str, Enum):
    """
    Enum representing types of devices available in the system.

    """
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


class ScheduleActionType(str, Enum):
    """
    Enum representing possible schedule actions for actuators.
    """
    WATER_ON = "WATER_ON"
    WATER_OFF = "WATER_OFF"
    ATOMIZE_ON = "ATOMIZE_ON"
    ATOMIZE_OFF = "ATOMIZE_OFF"
    FAN_ON = "FAN_ON"
    FAN_OFF = "FAN_OFF"
    HEATING_MAT_ON = "HEATING_MAT_ON"
    HEATING_MAT_OFF = "HEATING_MAT_OFF"


class ControlActionType(IntEnum):
    """
    Enum representing numeric identifiers for control actions.
    """
    WATER_ON = 0
    WATER_OFF = 1
    ATOMIZE_ON = 2
    ATOMIZE_OFF = 3
    FAN_ON = 4
    FAN_OFF = 5
    HEATING_MAT_ON = 6
    HEATING_MAT_OFF = 7
