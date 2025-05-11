from datetime import datetime
from pydantic import BaseModel


class NotificationCreateDTO(BaseModel):
    user_id: int
    message: str


class NotificationDTO(BaseModel):
    id: int
    user_id: int
    message: str
    created_at: datetime
    updated_at: datetime
