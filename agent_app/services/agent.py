import logging
from clients.backend_agent import BackendAgentClient

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self, backend_url: str, garden_id: int, access_token: str):
        self.backend_client = BackendAgentClient(
            garden_id, backend_url, access_token)

    async def action(self):
        logger.info("Agent is executed")
        devices = await self.backend_client.get_devices()

        logger.info(f"Devices: {devices}")
