from sqlalchemy.ext.asyncio import AsyncSession
from models.db import UserDb
from .utils.super_repo import SuperRepo


class UserRepository(SuperRepo[UserDb]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, UserDb)
