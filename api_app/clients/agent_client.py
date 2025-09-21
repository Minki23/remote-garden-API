import httpx
from exceptions.scheme import AppException


class AgentClient:
    def __init__(self, base_url: str = "http://agent:9000"):
        self.base_url = base_url.rstrip("/")

    async def trigger(self, refresh_token: str, garden_id: int) -> dict:
        payload = {
            "refresh_token": refresh_token,
            "garden_id": garden_id,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/agent/trigger", json=payload)

        if resp.status_code != 200:
            raise AppException(f"Agent service error: {resp.text}")

        try:
            return resp.json()
        except Exception:
            raise AppException("Invalid response from Agent service")
