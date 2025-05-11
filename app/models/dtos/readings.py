from datetime import datetime
from pydantic import BaseModel


class ReadingCreateDTO(BaseModel):
    device_id: int
    value: str


class ReadingDTO(BaseModel):
    id: int
    device_id: int
    value: str
    timestamp: datetime
