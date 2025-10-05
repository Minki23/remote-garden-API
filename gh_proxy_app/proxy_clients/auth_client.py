import os
from fastapi import HTTPException
import httpx

AUTH_API_URL = os.getenv("AUTH_API_URL", "http://localhost:3000/api")
AUTH_API_ENABLED = os.getenv("AUTH_API_ENABLED", "true").lower() == "true"


class AuthClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        await self.client.aclose()

    async def get_current_user(self, token: str) -> dict:
        """Get current user info from /me endpoint and verify admin status"""
        if not AUTH_API_ENABLED:
            return {
                "user_id": "dev-user",
                "is_admin": True,
                "email": "dev@example.com"
            }

        try:
            response = await self.client.get(
                f"{AUTH_API_URL}/users/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )

            if response.status_code == 200:
                user_data = response.json()

                # Check if user is admin
                if not user_data.get("is_admin", False):
                    raise HTTPException(
                        status_code=403,
                        detail="Admin access required"
                    )

                return user_data

            elif response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Authorization service error"
                )

        except httpx.RequestError as e:
            if AUTH_API_ENABLED:
                raise HTTPException(
                    status_code=503,
                    detail=f"Auth service unavailable: {str(e)}"
                )
            # Fallback for development
            return {
                "user_id": "fallback-user",
                "is_admin": True,
                "email": "fallback@example.com"
            }
