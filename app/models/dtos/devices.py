from datetime import datetime
from pydantic import BaseModel
from models.enums import DeviceType


class DeviceCreateDTO(BaseModel):
    garden_id: int
    mac: str
    device_type: DeviceType


class DeviceDTO(BaseModel):
    id: int
    garden_id: int
    mac: str
    device_type: DeviceType
    created_at: datetime
    updated_at: datetime
