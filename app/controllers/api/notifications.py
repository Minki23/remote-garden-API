from fastapi import APIRouter
from app.core.dependencies import NotificationServiceDep
from app.models.dtos.notifications import NotificationCreateDTO, NotificationDTO

router = APIRouter()


@router.post("/", response_model=NotificationDTO)
async def create_notification(dto: NotificationCreateDTO, service: NotificationServiceDep):
    return await service.create(dto)


@router.get("/user/{user_id}", response_model=list[NotificationDTO])
async def get_by_user(user_id: int, service: NotificationServiceDep):
    return await service.get_by_user(user_id)
