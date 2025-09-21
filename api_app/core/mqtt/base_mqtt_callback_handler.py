import re
import logging
from typing import Self

from exceptions.scheme import AppException

logger = logging.getLogger(__name__)


class BaseMqttCallbackHandler:
    _instance: Self | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, topic_template: str):
        if getattr(self, "_initialized", False):
            return

        # e.g., "device/{device_id}/status"
        self.topic_template = topic_template
        self._initialized = True

    @property
    def wildcard_topic(self) -> str:
        """
        Replaces all `{...}` placeholders with MQTT `+` wildcard.
        E.g., "device/{device_id}/status" -> "device/+/status"
        """
        return re.sub(r"\{[^{}]+\}", "+", self.topic_template)

    def get_concrete_topic(self, **kwargs) -> str:
        """
        Returns the concrete topic based on provided values.
        E.g., get_concrete_topic(device_id=42) -> "device/42/status"
        """
        return self.topic_template.format(**kwargs)

    async def __call__(self, topic: str, payload: dict):
        raise NotImplementedError("Subclasses must implement __call__")

    async def last_message_of_topic(self, **kwargs) -> str | None:
        from core.mqtt.mqtt_subscriber import MqttTopicSubscriber

        return MqttTopicSubscriber().get_last_message(self.get_concrete_topic(**kwargs))

    def extract_from_topic(self, topic: str, key: str) -> str | None:
        """
        Extracts a value from a concrete topic based on the topic_template and given key.
        E.g., for template 'device/{garden_id}/co2' and topic 'device/42/co2',
        extract_from_topic(topic, 'garden_id') -> '42'
        """
        pattern = re.escape(self.topic_template)
        pattern = re.sub(r"\\\{([^{}]+)\\\}", r"(?P<\1>[^/]+)", pattern)
        match = re.match(pattern, topic)
        if not match:
            raise AppException(
                f"Topic '{topic}' does not match template '{self.topic_template}'"
            )
        return match.groupdict().get(key)
