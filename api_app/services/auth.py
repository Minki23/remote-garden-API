from datetime import datetime, timedelta
import secrets
from core.config import CONFIG
from exceptions.scheme import AppException
from repos.users import UserRepository
from core.security.google import verify_google_token
from core.security.jwt import create_access_token_for_user, create_refresh_token
from models.dtos.auth import TokenDTO


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def login_with_google(self, id_token: str) -> TokenDTO:
        claims = await verify_google_token(id_token)
        email = claims["email"]
        sub = claims["sub"]

        user = await self.repo.get_by_google_sub(sub)
        if not user:
            user = await self.repo.create(
                email=email,
                google_sub=sub,
                auth=secrets.token_urlsafe(32)
            )

        access_token = create_access_token_for_user(user.id)
        refresh_token = create_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=CONFIG.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.repo.save_refresh_token(user.id, refresh_token, expires_at)

        return TokenDTO(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: str) -> TokenDTO:
        user = await self.repo.get_by_refresh_token(refresh_token)
        if not user:
            raise AppException("Invalid refresh token")

        if not user.refresh_expires_at or user.refresh_expires_at < datetime.utcnow():
            raise AppException("Refresh token expired")

        access_token = create_access_token_for_user(user.id)
        return TokenDTO(access_token=access_token, refresh_token=refresh_token)
