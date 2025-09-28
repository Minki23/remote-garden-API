import logging
from agent_clients.backend_token import BackendTokenClient
from agent_models.agent_token import AgentTokenDTO as TokenDTO

logger = logging.getLogger(__name__)


class TokenService:
    """
    Service for handling authentication tokens.
    """

    def __init__(self, backend_url: str):
        """
        Initialize the TokenService.

        Args:
            backend_url (str): Base URL of the backend service.
        """
        self.backend_client = BackendTokenClient(backend_url)

    async def register_token(self, token: str) -> TokenDTO:
        """
        Register a refresh token and obtain an access token.

        Args:
            token (str): The refresh token provided by the client.

        Raises:
            ValueError: If no refresh token is provided.

        Returns:
            TokenDTO: Data object containing the new access token.
        """
        if not token:
            raise ValueError("Missing refresh token")

        logger.info(f"Registered refresh token: {token}")

        return await self._fetch_access_token(token)

    async def _fetch_access_token(self, refresh_token: str) -> TokenDTO:
        """
        Internal helper to request a new access token from the backend.

        Args:
            refresh_token (str): The refresh token used to obtain a new access token.

        Returns:
            TokenDTO: Data object with the access token.
        """
        token_data = await self.backend_client.refresh_access_token(refresh_token)
        token = TokenDTO(**token_data)
        self.access_token = token.access_token
        return token
