from models.db import NotificationDb
from models.dtos.notifications import NotificationDTO


def db_to_dto(notification: NotificationDb) -> NotificationDTO:
    return NotificationDTO(
        id=notification.id,
        user_id=notification.user_id,
        message=notification.message,
        type=notification.type,
        read=notification.read,
        created_at=notification.created_at,
        updated_at=notification.updated_at,
    )
