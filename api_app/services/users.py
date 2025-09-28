from models.dtos.users import UserDTO
from mappers.users import db_to_user_dto
from repos.users import UserRepository
from exceptions.scheme import AppException


class UserService:
    """
    Service for managing user accounts.

    Provides methods for retrieving and deleting user records.
    """

    def __init__(self, repo: UserRepository):
        """
        Initialize the service with a user repository.
        """
        self.repo = repo

    async def get_user(self, user_id: int) -> UserDTO:
        """
        Retrieve a user by ID.

        Parameters
        ----------
        user_id : int
            ID of the user to fetch.

        Returns
        -------
        UserDTO
            The user data as a DTO.

        Raises
        ------
        AppException
            If the user does not exist.
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise AppException(message="User not found", status_code=404)
        return db_to_user_dto(user)

    async def delete_user(self, user_id: int) -> None:
        """
        Delete a user by ID.

        Parameters
        ----------
        user_id : int
            ID of the user to delete.

        Raises
        ------
        AppException
            If the user does not exist.
        """
        deleted = await self.repo.delete(user_id)
        if not deleted:
            raise AppException(message="User not found", status_code=404)
