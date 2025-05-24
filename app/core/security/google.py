from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.core.config import CONFIG
import httpx

async def verify_google_token(id_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        )
        if response.status_code != 200:
            raise ValueError("Invalid Google token")
        data = response.json()
        if data["aud"] != CONFIG.GOOGLE_CLIENT_ID:
            raise ValueError("Invalid audience")
        return data
