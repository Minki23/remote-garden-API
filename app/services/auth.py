from sqlalchemy.ext.asyncio import AsyncSession
from app.repos.users import UserRepository
from app.core.security.google import verify_google_token
from app.core.security.jwt import create_access_token
from app.models.dtos.auth import TokenDTO


class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def login_with_google(self, id_token: str) -> TokenDTO:
        claims = await verify_google_token(id_token)
        email = claims["email"]
        sub = claims["sub"]

        user = await self.repo.get_by_google_sub(sub)
        if not user:
            user = await self.repo.create(email=email, google_sub=sub)

        jwt_token = create_access_token({"sub": str(user.id)})
        return TokenDTO(access_token=jwt_token)
