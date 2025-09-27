from common_db import db
from models.dtos.users import UserDTO


def db_to_user_dto(user: db.UserDb) -> UserDTO:
    """
    Convert a UserDb ORM object to a UserDTO.
    """
    return UserDTO(
        id=user.id,
        email=user.email,
        updated_at=user.updated_at,
        created_at=user.created_at,
        auth=user.auth,
        admin=user.admin,
    )
