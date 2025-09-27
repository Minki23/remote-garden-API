from contextlib import asynccontextmanager
from typing import Callable, Awaitable
from fastapi import FastAPI
import asyncio
import logging

from core.mqtt.mqtt_subscriber import MqttTopicSubscriber

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(
    app: FastAPI, topic_subscribe_callback: Callable[[], Awaitable[None]]
):
    """
    Manage application lifespan with MQTT subscriber.

    Starts an MQTT subscriber in the background when the FastAPI app starts,
    subscribes to topics, and ensures proper cleanup when the app shuts down.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.
    topic_subscribe_callback : Callable[[], Awaitable[None]]
        A coroutine to register topic handlers after subscriber startup.

    Yields
    ------
    None
        Allows FastAPI lifespan integration to continue execution.
    """
    logger.info("Starting MQTT subscriber...")
    subscriber = MqttTopicSubscriber()
    task = asyncio.create_task(subscriber.start())

    # Short delay to ensure the subscriber is running before subscribing
    await asyncio.sleep(1)

    await topic_subscribe_callback()

    try:
        yield
    finally:
        logger.info("Shutting down MQTT subscriber...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("MQTT subscriber cancelled.")
