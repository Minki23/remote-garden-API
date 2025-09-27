import asyncio
import json
import logging
from collections import defaultdict, deque
from typing import Callable, Awaitable, Dict, Self
from aiomqtt import Client, Message
from core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler
from core.mqtt.tls_context import create_tls_context
from core.config import CONFIG
from exceptions.scheme import AppException

logger = logging.getLogger(__name__)


class MqttTopicSubscriber:
    """
    MQTT topic subscriber using aiomqtt.

    Maintains history of received messages and dispatches them to registered callbacks.
    Implemented as a singleton, so all calls share the same underlying client instance.
    """

    _instance: Self | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the MQTT subscriber.

        Broker host and port are taken from CONFIG.
        """
        if getattr(self, "_initialized", False):
            return

        self.broker_host = CONFIG.MQTT_BROKER_HOST
        self.port = CONFIG.MQTT_BROKER_PORT
        self._history: Dict[str, deque[dict]] = defaultdict(
            lambda: deque(maxlen=5))
        self._callbacks: Dict[str, list[Callable[[
            str, dict], Awaitable[None]]]] = defaultdict(list)
        self._client: Client | None = None
        self.tls_context = create_tls_context()
        self._initialized = True

    async def start(self):
        """
        Connect to the MQTT broker and start listening for messages.

        This method blocks until the connection is closed.
        """
        logger.info(
            f"Connecting to MQTT broker at {self.broker_host}:{self.port}")
        self._client = Client(
            self.broker_host,
            port=self.port,
            tls_context=self.tls_context,
        )

        async with self._client as client:
            async for message in client.messages:
                try:
                    await self._handle_message(message)
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                finally:
                    logger.info(f"Message processed: {message.topic}")

        logger.info("MQTT client disconnected")

    async def subscribe(
        self,
        topic: str,
        callback: Callable[[str, dict], Awaitable[None]] | None = None,
    ):
        """
        Subscribe to a specific topic.

        Parameters
        ----------
        topic : str
            MQTT topic to subscribe to.
        callback : Callable[[str, dict], Awaitable[None]] | None
            Optional callback to handle incoming messages.
        """
        if self._client is None:
            raise RuntimeError("Client is not connected yet")

        await self._client.subscribe(topic)
        logger.info(f"Subscribed to topic: {topic}")

        if callback:
            self._callbacks[topic].append(callback)
        else:
            logger.warning(f"No callback provided for topic {topic}.")

    async def subscribe_handler(self, handler: BaseMqttCallbackHandler):
        """
        Subscribe using a handler object.

        Parameters
        ----------
        handler : BaseMqttCallbackHandler
            A handler implementing the __call__ method for incoming messages.
        """
        await self.subscribe(handler.wildcard_topic, handler)

    async def _handle_message(self, message: Message):
        """
        Internal method to process a single MQTT message.
        Dispatches to all callbacks matching the topic.
        """
        raw_payload = message.payload.decode()
        topic = str(message.topic)

        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON on topic {topic}: {raw_payload} ({e})")
            return

        logger.info(f"[MQTT IN] {topic}: {payload}")
        self._history[topic].append(payload)

        for pattern, callbacks in self._callbacks.items():
            if self._topic_matches(pattern, topic):
                for callback in callbacks:
                    await callback(topic, payload)

    def get_last_messages(self, topic: str) -> list[dict]:
        """
        Return the last few messages for a given topic.
        """
        return list(self._history[topic])

    def get_last_message(self, topic: str) -> dict:
        """
        Return the most recent message for a given topic.

        Raises
        ------
        AppException
            If no message exists for the topic.
        """
        if not self._history[topic]:
            raise AppException(f"No message found for topic: {topic}")
        return self._history[topic][-1]

    def _topic_matches(self, pattern: str, topic: str) -> bool:
        """
        Check if a topic matches a subscription pattern.

        Supports MQTT wildcards '+' and '#'.
        """
        pattern_parts = pattern.split("/")
        topic_parts = topic.split("/")

        for p, t in zip(pattern_parts, topic_parts):
            if p == "#":
                return True
            if p == "+":
                continue
            if p != t:
                return False

        return len(pattern_parts) == len(topic_parts)


if __name__ == "__main__":

    async def on_message(topic: str, payload: dict):
        print(
            f"[ACTION] New message on {topic}: {json.dumps(payload, indent=2)}")

    async def main():
        subscriber = MqttTopicSubscriber()

        async def run():
            await subscriber.subscribe("device/1/status", on_message)
            await subscriber.subscribe("device/2/status", on_message)

        await asyncio.gather(subscriber.start(), run())

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
