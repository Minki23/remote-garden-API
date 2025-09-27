import re
import logging
from exceptions.scheme import AppException

logger = logging.getLogger(__name__)


class BaseMqttCallbackHandler:
    """
    Base class for MQTT callback handlers.
    Provides utilities for working with MQTT topics
    defined via templates (with placeholders).
    """

    def __init__(self, topic_template: str):
        """
        Initialize handler with a topic template.

        Parameters
        ----------
        topic_template : str
            Template for MQTT topics, e.g. "device/{device_id}/status".
        """
        self.topic_template = topic_template

    @property
    def wildcard_topic(self) -> str:
        """
        Returns a topic string with placeholders replaced by MQTT '+' wildcard.

        Example
        -------
        "device/{device_id}/status" -> "device/+/status"
        """
        return re.sub(r"\{[^{}]+\}", "+", self.topic_template)

    def get_concrete_topic(self, **kwargs) -> str:
        """
        Build a concrete topic from the template with provided values.

        Example
        -------
        get_concrete_topic(device_id=42)
        -> "device/42/status"
        """
        try:
            return self.topic_template.format(**kwargs)
        except KeyError as e:
            raise AppException(
                f"Missing key {e.args[0]} for topic template") from e

    async def __call__(self, topic: str, payload: dict):
        """
        Must be implemented by subclasses to handle incoming MQTT messages.
        """
        raise NotImplementedError("Subclasses must implement __call__")

    async def last_message_of_topic(self, **kwargs) -> str | None:
        """
        Get the last retained message for a topic built from the template.

        Returns
        -------
        str | None
            Last message content if available.
        """
        from core.mqtt.mqtt_subscriber import MqttTopicSubscriber
        return MqttTopicSubscriber().get_last_message(self.get_concrete_topic(**kwargs))

    def extract_from_topic(self, topic: str, key: str) -> str:
        """
        Extract a value from a topic string based on the template.

        Example
        -------
        Template: "device/{garden_id}/co2"
        Topic:    "device/42/co2"
        extract_from_topic(..., "garden_id") -> "42"
        """
        pattern = re.escape(self.topic_template)
        pattern = re.sub(r"\\\{([^{}]+)\\\}", r"(?P<\1>[^/]+)", pattern)
        match = re.match(pattern, topic)

        if not match:
            logger.error(
                f"Topic '{topic}' does not match template '{self.topic_template}'")
            raise AppException(
                f"Topic '{topic}' does not match template '{self.topic_template}'")

        return match.groupdict().get(key)
