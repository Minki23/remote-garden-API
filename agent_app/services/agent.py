import logging
from clients.backend_agent import BackendAgentClient

logger = logging.getLogger(__name__)


class AgentService:
    """
    Service responsible for executing agent actions within a garden.

    This service acts as a wrapper around :class:`BackendAgentClient` and 
    contains the application logic for interacting with backend devices.
    """

    def __init__(self, backend_url: str, garden_id: int, access_token: str):
        """
        Initialize the AgentService.

        Args:
            backend_url (str): Base URL of the backend service.
            garden_id (int): Identifier of the garden on which the agent operates.
            access_token (str): Access token for authenticating with the backend API.
        """
        self.backend_client = BackendAgentClient(
            garden_id, backend_url, access_token
        )

    async def action(self):
        """
        Execute the agent's main action.

        Returns:
            list: A list of devices retrieved from the backend (@TODO whole logic)
        """
        logger.info("Agent is executed")
        devices = await self.backend_client.get_devices()
        # @TODO add logic

        logger.info(f"Devices: {devices}")
        return devices
