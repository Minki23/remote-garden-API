from pydantic import BaseModel
from common_db.enums import DeviceType


class DeviceDTO(BaseModel):
    id: int
    type: DeviceType
