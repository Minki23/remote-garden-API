from app.models import db
from app.models.dtos.users import UserDTO


def db_to_user_dto(user: db.UserDb) -> UserDTO:
    return UserDTO(
        id=user.id,
        email=user.email,
        updated_at=user.updated_at,
        created_at=user.created_at,
        auth=user.auth,
        admin=user.admin
    )
