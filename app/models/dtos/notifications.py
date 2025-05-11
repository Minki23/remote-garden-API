from datetime import datetime
from pydantic import BaseModel
from ..enums import NotificationType

class NotificationCreateDTO(BaseModel):
    user_id: int
    message: str


class NotificationDTO(BaseModel):
    id: int
    user_id: int
    message: str
    read: bool
    type: NotificationType
    created_at: datetime
    updated_at: datetime
