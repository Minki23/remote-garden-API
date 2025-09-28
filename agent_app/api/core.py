import asyncio
from fastapi import APIRouter
from agent_services.agent import AgentService
from agent_services.token import TokenService
from agent_models.trigger import ApiTriggerDTO as TriggerDTO
import logging
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://app:3000/api")

service = TokenService(backend_url=BACKEND_URL)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/trigger")
async def trigger(trigger: TriggerDTO):
    """
    Endpoint for triggering agent actions.

    Args:
        trigger (ApiTriggerDTO): Object containing `refresh_token`, `garden_id` and `context`.

    Returns:
        dict: JSON response `{"status": "triggered"}` when the trigger is accepted.

    Details:
        The function registers a new token, creates an instance of `AgentService`,
        and starts an asynchronous background task to perform the action without blocking the request.
    """
    token = (await service.register_token(trigger.refresh_token)).access_token
    agent = AgentService(BACKEND_URL, trigger.garden_id, token)

    async def worker():
        try:
            success = await agent.action(trigger.context)
            logger.info(f"Action finished: {success}")
        except Exception as e:
            logger.error(f"Error: {e}")

    asyncio.create_task(worker())

    return {"status": "triggered"}
