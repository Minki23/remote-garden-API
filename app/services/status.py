from app.controllers.mqtt_handlers.status_handler import DeviceStatusHandler
from app.core.mqtt.mqtt_subscriber import MqttTopicSubscriber
from app.models.enums import DeviceType
from app.models.dtos.status import StatusDTO


class StatusService:
    async def get_status(self, type: DeviceType, garden_id: str) -> StatusDTO:
        status = await DeviceStatusHandler().last_message_of_topic(garden_id=garden_id)

        return StatusDTO(**status)
