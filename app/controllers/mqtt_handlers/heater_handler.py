from app.controllers.mqtt_handlers.common.device_reading_handler import (
    DeviceReadingHandler,
)
from app.models.enums import DeviceType


class HeaterHandler(DeviceReadingHandler):
    def __init__(self):
        super().__init__("device/{garden_id}/heater", DeviceType.HEATER)
