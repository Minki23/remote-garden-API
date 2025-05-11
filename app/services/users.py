from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models.dtos.users import UserCreateDTO, UserDTO
from mappers.users import db_to_user_dto
from repos.users import UserRepository
from exceptions.scheme import AppException


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, data: UserCreateDTO) -> UserDTO:
        try:
            user = await self.repo.create(email=data.email)
        except IntegrityError:
            raise AppException(message="Email already exists", status_code=422)

        return db_to_user_dto(user)

    async def delete_user(self, user_id: int) -> None:
        deleted = await self.repo.delete(user_id)
        if not deleted:
            raise AppException(message="User not found", status_code=404)

    async def get_user(self, user_id: int) -> UserDTO:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise AppException(message="User not found", status_code=404)
        return db_to_user_dto(user)
