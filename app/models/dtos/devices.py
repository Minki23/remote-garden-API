from datetime import datetime
from pydantic import BaseModel
from app.models.enums import DeviceType


class DeviceDTO(BaseModel):
    id: int
    type: DeviceType
