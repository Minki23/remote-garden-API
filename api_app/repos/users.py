from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from common_db.db import GardenDb, UserDb
from .utils.super_repo import SuperRepo
from sqlalchemy.future import select

from datetime import datetime
from core.security.jwt import hash_refresh_token


class UserRepository(SuperRepo[UserDb]):
    """
    Repository for managing users and authentication-related data.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db, UserDb)

    async def get_by_google_sub(self, sub: str) -> Optional[UserDb]:
        """
        Return a user by Google account sub (subject).
        """
        result = await self.db.execute(
            select(self.model).where(self.model.google_sub == sub)
        )
        return result.scalar_one_or_none()

    async def get_by_garden_id(self, garden_id: int) -> Optional[UserDb]:
        """
        Return the user who owns a given garden.
        """
        stmt = select(UserDb).join(UserDb.gardens).where(
            GardenDb.id == garden_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_key(self, user_key: str) -> Optional[UserDb]:
        """
        Return a user by their authentication key.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.auth == user_key)
        )
        return result.scalar_one_or_none()

    async def save_refresh_token(
        self, user_id: int, token: str, expires_at: datetime
    ) -> Optional[UserDb]:
        """
        Store a hashed refresh token and its expiry for the given user.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.refresh_token_hash = hash_refresh_token(token)
        user.refresh_expires_at = expires_at
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_refresh_token(self, token: str) -> Optional[UserDb]:
        """
        Return a user matching the given refresh token.
        """
        token_hash = hash_refresh_token(token)
        result = await self.db.execute(
            select(self.model).where(
                self.model.refresh_token_hash == token_hash)
        )
        return result.scalar_one_or_none()
