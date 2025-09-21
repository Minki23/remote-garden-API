from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db import GardenDb, UserDb
from .utils.super_repo import SuperRepo
from sqlalchemy.future import select


from datetime import datetime
from app.core.security.jwt import hash_refresh_token


class UserRepository(SuperRepo[UserDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, UserDb)

    async def get_by_google_sub(self, sub: str) -> Optional[UserDb]:
        result = await self.db.execute(
            select(self.model).where(self.model.google_sub == sub)
        )
        return result.scalar_one_or_none()

    async def get_by_garden_id(self, garden_id: int) -> Optional[UserDb]:
        stmt = select(UserDb).join(UserDb.gardens).where(
            GardenDb.id == garden_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_key(self, user_key: str) -> Optional[UserDb]:
        result = await self.db.execute(
            select(self.model).where(self.model.auth == user_key)
        )
        return result.scalar_one_or_none()

    async def save_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> Optional[UserDb]:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.refresh_token_hash = hash_refresh_token(token)
        # user.refresh_token_hash = token
        user.refresh_expires_at = expires_at
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_refresh_token(self, token: str) -> Optional[UserDb]:
        token_hash = hash_refresh_token(token)
        result = await self.db.execute(
            select(self.model).where(
                self.model.refresh_token_hash == token_hash)
        )
        return result.scalar_one_or_none()
