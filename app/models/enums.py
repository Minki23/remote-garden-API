from enum import Enum


class DeviceType(str, Enum):
    SENSOR = "SENSOR"
    PUMP = "PUMP"
    LIGHT = "LIGHT"
    OTHER = "OTHER"


class NotificationType(str, Enum):
    alert = "alert"
    reminder = "reminder"
    system = "system"
