import logging
from clients.backend_token import BackendTokenClient
from models.token import TokenDTO

logger = logging.getLogger(__name__)


class TokenService:
    def __init__(self, backend_url: str):
        self.backend_client = BackendTokenClient(backend_url)

    async def register_token(self, token: str) -> TokenDTO:
        if not token:
            raise ValueError("Missing refresh token")

        logger.info(f"Registered refresh token: {token}")

        return await self._fetch_access_token(token)

    async def _fetch_access_token(self, refresh_token: str) -> TokenDTO:
        token_data = await self.backend_client.refresh_access_token(refresh_token)
        token = TokenDTO(**token_data)
        self.access_token = token.access_token
        return token
