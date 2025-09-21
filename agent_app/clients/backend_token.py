import httpx
from app.exceptions.scheme import AppException


class BackendTokenClient:
    def __init__(self, base_url: str = "http://backend:8000"):
        self.base_url = base_url.rstrip("/")

    async def refresh_access_token(self, refresh_token: str) -> dict:
        payload = {"refresh_token": refresh_token}

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/agents/refresh", json=payload)

        if resp.status_code != 200:
            raise AppException(f"Backend error: {resp.text}")

        data = resp.json()
        if "access_token" not in data:
            raise AppException("Invalid response from backend")

        return data
