from .status_handler import StatusHandler
from .actuator_confirm_handler import ActuatorConfirmHandler
from .conn_handler import ConnHandler
from .device_reading_handler import DeviceReadingHandler

from core.mqtt.mqtt_subscriber import MqttTopicSubscriber


async def subscribe_topics():
    for handler in (
        DeviceReadingHandler,
        ConnHandler,
        ActuatorConfirmHandler,
        StatusHandler,
    ):
        await MqttTopicSubscriber().subscribe_handler(handler())


__all__ = ["subscribe_topics"]
