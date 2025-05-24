from contextlib import asynccontextmanager
from typing import Callable, Awaitable
from fastapi import FastAPI
import asyncio
import logging

from app.core.mqtt.mqtt_subscriber import MqttTopicSubscriber

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI, topic_subscribe_callback: Callable[[], Awaitable[None]]):
    logger.info("Starting MQTT subscriber...")
    subscriber = MqttTopicSubscriber()
    task = asyncio.create_task(subscriber.start())

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
