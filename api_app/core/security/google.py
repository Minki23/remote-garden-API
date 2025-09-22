from authlib.integrations.httpx_client import AsyncOAuth2Client
from core.config import CONFIG
import httpx

from exceptions.scheme import GoogleAuthException


async def verify_google_token(id_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        )
        if response.status_code != 200:
            raise GoogleAuthException("Invalid Google token")
        data = response.json()
        if data["aud"] != CONFIG.GOOGLE_CLIENT_ID:
            raise GoogleAuthException("Invalid audience")
        return data
