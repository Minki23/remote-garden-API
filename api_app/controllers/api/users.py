from fastapi import APIRouter, status
from core.dependencies import UserServiceDep, CurrentUserDep
from models.dtos.users import UserDTO

router = APIRouter()


@router.get("/me", response_model=UserDTO)
async def get_current_user(service: UserServiceDep, user_id: CurrentUserDep) -> UserDTO:
    """
    Retrieve details of the currently authenticated user.
    Provides user profile data from the database.
    """
    return await service.get_user(user_id)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(user_id: CurrentUserDep, service: UserServiceDep) -> None:
    """
    Delete the account of the current user.
    This action permanently removes user data.
    """
    await service.delete_user(user_id)
