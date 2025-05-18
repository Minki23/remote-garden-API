from datetime import datetime
from pydantic import BaseModel
from app.models.enums import DeviceType


class DeviceCreateDTO(BaseModel):
    garden_id: int
    mac: str
    type: DeviceType


class DeviceDTO(BaseModel):
    id: int
    garden_id: int
    mac: str
    type: DeviceType
    created_at: datetime
    updated_at: datetime
