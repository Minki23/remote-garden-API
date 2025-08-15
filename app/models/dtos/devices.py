from datetime import datetime
from pydantic import BaseModel
from app.models.enums import DeviceType


class DeviceDTO(BaseModel):
    id: int
    garden_id: int
    type: DeviceType
    created_at: datetime
    updated_at: datetime
