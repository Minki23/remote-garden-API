from app.controllers.mqtt_handlers.common.device_reading_handler import (
    DeviceReadingHandler,
)
from app.models.enums import DeviceType


class RoofHandler(DeviceReadingHandler):
    def __init__(self):
        super().__init__("device/{garden_id}/roof", DeviceType.ROOF)
