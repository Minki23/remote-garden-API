from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.core.mqtt.mqtt_client import mqtt_listener
import asyncio
# from db import context

import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Provides a context manager for managing the lifespan of a FastAPI application.

    Inside the `lifespan` context manager, the `before start` and `before stop`
    comments indicate where the startup and shutdown operations should be
    implemented.
    """

    logger.info("Starting MQTT listener...")
    logger.info("Starting lifespan of the app...")

    task = asyncio.create_task(mqtt_listener())

    # before start
    yield
    # before stop

    task.cancel()
