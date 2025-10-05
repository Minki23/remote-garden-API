import base64
import logging
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
import httpx

logger = logging.getLogger(__name__)


class ProxyAuthService:
    """Service handling authentication and authorization."""

    def __init__(self, auth_api_url: str, auth_api_enabled: bool):
        self.auth_api_url = auth_api_url
        self.auth_api_enabled = auth_api_enabled
        self.auth_client = httpx.AsyncClient(timeout=30.0)

    async def validate_user_token(self, token: str) -> dict:
        """Validate user token via auth API."""
        if not self.auth_api_enabled:
            logger.info(">>> Auth disabled, allowing access")
            return {"user_id": "dev-user", "is_admin": True}

        try:
            response = await self.auth_client.get(
                f"{self.auth_api_url}/users/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )

            if response.status_code == 200:
                user_data = response.json()
                if not user_data.get("is_admin", False):
                    raise HTTPException(
                        status_code=403, detail="Admin access required")
                return user_data
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=401, detail="Invalid or expired token")
            else:
                raise HTTPException(
                    status_code=500, detail="Authorization service error")

        except httpx.RequestError as e:
            logger.error(f"Auth service error: {e}")
            if self.auth_api_enabled:
                raise HTTPException(
                    status_code=503, detail="Auth service unavailable")
            return {"user_id": "fallback-user", "is_admin": True}

    def extract_bearer_token(self, credentials: HTTPAuthorizationCredentials) -> str:
        """Extract Bearer token from credentials."""
        return credentials.credentials

    def extract_basic_auth_token(self, auth_header: str) -> str:
        """Extract token from Basic Auth header."""
        if not auth_header or not auth_header.lower().startswith("basic "):
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            encoded = auth_header.split(" ", 1)[1]
            decoded = base64.b64decode(encoded).decode()
            username, token = decoded.split(":", 1)
            return token
        except Exception:
            raise HTTPException(
                status_code=401, detail="Invalid Basic Auth header")

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """Extract and validate Bearer token from Authorization header."""
        token = self.extract_bearer_token(credentials)
        return await self.validate_user_token(token)

    async def get_current_user_from_header(self, request: Request) -> dict:
        """Extract and validate Bearer token from request header (for registry endpoints)."""
        auth_header = request.headers.get("authorization")
        token = self.extract_basic_auth_token(auth_header)
        return await self.validate_user_token(token)

    async def close(self):
        """Close the HTTP client."""
        await self.auth_client.aclose()
