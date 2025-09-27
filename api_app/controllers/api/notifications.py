from fastapi import APIRouter
from core.dependencies import (
    CurrentUserDep,
    NotificationServiceDep,
    UserNotificationDep,
)
from models.dtos.notifications import NotificationDTO

router = APIRouter()


@router.get("/", response_model=list[NotificationDTO])
async def get_by_user(service: NotificationServiceDep, user_id: CurrentUserDep):
    """
    Retrieve all notifications for the current user.
    """
    return await service.get_by_user(user_id)


@router.patch("/{id}/dismiss/", response_model=bool)
async def dismiss_notification(
    notif: UserNotificationDep,
    service: NotificationServiceDep,
):
    """
    Mark a specific notification as dismissed.
    Requires ownership validation by user ID.
    """
    return await service.dismiss(notif.id, notif.user_id)


@router.get("/alerts/", response_model=list[NotificationDTO])
async def get_alerts(user_id: CurrentUserDep, service: NotificationServiceDep):
    """
    Retrieve all alert-type notifications for the user.
    Useful for urgent garden-related warnings.
    """
    return await service.get_by_user_and_type(user_id, "alert")


@router.get("/reminders/", response_model=list[NotificationDTO])
async def get_reminders(user_id: CurrentUserDep, service: NotificationServiceDep):
    """
    Retrieve all reminder notifications for the user.
    Includes tasks, schedules, and periodic prompts.
    """
    return await service.get_by_user_and_type(user_id, "reminder")


@router.get("/system/", response_model=list[NotificationDTO])
async def get_system_notifications(
    user_id: CurrentUserDep, service: NotificationServiceDep
):
    """
    Retrieve all system-level notifications.
    Typically includes maintenance or service messages.
    """
    return await service.get_by_user_and_type(user_id, "system")
