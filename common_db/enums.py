from enum import Enum, IntEnum


class DeviceType(str, Enum):
    """
    Represents the different types of devices supported by the system.
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


class NotificationType(str, Enum):
    """
    Represents the different types of system notifications.
    """
    alert = "alert"
    reminder = "reminder"
    system = "system"


class ScheduleActionType(str, Enum):
    """
    Represents actions that can be scheduled for garden devices.
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
    Represents low-level control actions mapped to device commands.
    """
    WATER_ON = 0
    WATER_OFF = 1
    ATOMIZE_ON = 2
    ATOMIZE_OFF = 3
    FAN_ON = 4
    FAN_OFF = 5
    HEATING_MAT_ON = 6
    HEATING_MAT_OFF = 7
