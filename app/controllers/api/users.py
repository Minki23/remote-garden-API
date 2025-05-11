from fastapi import APIRouter, status
from core.dependencies import UserServiceDep, CurrentUserDep
from models.dtos.users import UserCreateDTO, UserDTO

router = APIRouter()


@router.post("/", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def create_user(dto: UserCreateDTO, service: UserServiceDep) -> UserDTO:
    return await service.create_user(dto)


@router.get("/me", response_model=UserDTO)
async def get_current_user(user_id: CurrentUserDep, service: UserServiceDep) -> UserDTO:
    return await service.get_user(user_id)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(user_id: CurrentUserDep, service: UserServiceDep) -> None:
    await service.delete_user(user_id)
