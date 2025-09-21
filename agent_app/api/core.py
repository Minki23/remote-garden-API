import asyncio
from fastapi import APIRouter
from services.agent import AgentService
from services.token import TokenService
from models.trigger import TriggerDTO
import logging
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://app:3000/api")

service = TokenService(backend_url=BACKEND_URL)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/trigger")
async def trigger(trigger: TriggerDTO):
    token = (await service.register_token(trigger.refresh_token)).access_token
    agent = AgentService(BACKEND_URL, trigger.garden_id, token)

    async def worker():
        try:
            success = await agent.action()
            logger.info(f"Action finished: {success}")
        except Exception as e:
            logger.error(f"Error: {e}")

    asyncio.create_task(worker())

    return {"status": "triggered"}
