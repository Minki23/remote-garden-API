import httpx


class BackendTokenClient:
    """Client for handling token refresh operations with the backend API."""

    def __init__(self, base_url: str = "http://backend:8000"):
        """Initialize the token client.

        Args:
            base_url (str, optional): Backend base URL. Defaults to ``"http://backend:8000"``.
        """
        self.base_url = base_url.rstrip("/")

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Request a new access token using a refresh token.

        Args:
            refresh_token (str): The refresh token issued by the backend.

        Returns:
            dict: A dictionary containing at least the new ``access_token``.

        Raises:
            httpx.HTTPStatusError: If the backend responds with an error status.
            httpx.ProtocolError: If the backend response does not contain ``access_token``.
        """
        payload = {"refresh_token": refresh_token}

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/agents/refresh", json=payload)

        if resp.status_code != 200:
            raise httpx.HTTPStatusError(
                f"Backend error: {resp.text}",
                request=resp.request,
                response=resp
            )

        data = resp.json()
        if "access_token" not in data:
            raise httpx.ProtocolError("Invalid response from backend")

        return data
