from pydantic import BaseModel
from models.enums import DeviceType


class DeviceDTO(BaseModel):
    id: int
    type: DeviceType
