from fastapi import APIRouter
from app.core.dependencies import (
    CurrentUserDep,
    NotificationServiceDep,
    UserNotificationDep,
)
from app.models.dtos.notifications import NotificationCreateDTO, NotificationDTO

router = APIRouter()


# @router.post("/", response_model=NotificationDTO)
# async def create_notification(dto: NotificationCreateDTO, service: NotificationServiceDep):
#     return await service.create(dto)


@router.get("/", response_model=list[NotificationDTO])
async def get_by_user(service: NotificationServiceDep, user_id: CurrentUserDep):
    return await service.get_by_user(user_id)


@router.patch("/{id}/dismiss/", response_model=bool)
async def dismiss_notification(
    notif: UserNotificationDep,
    service: NotificationServiceDep,
):
    return await service.dismiss(notif.id, notif.user_id)


@router.get("/alerts/", response_model=list[NotificationDTO])
async def get_alerts(user_id: CurrentUserDep, service: NotificationServiceDep):
    return await service.get_by_user_and_type(user_id, "alert")


@router.get("/reminders/", response_model=list[NotificationDTO])
async def get_reminders(user_id: CurrentUserDep, service: NotificationServiceDep):
    return await service.get_by_user_and_type(user_id, "reminder")


@router.get("/system/", response_model=list[NotificationDTO])
async def get_system_notifications(
    user_id: CurrentUserDep, service: NotificationServiceDep
):
    return await service.get_by_user_and_type(user_id, "system")
