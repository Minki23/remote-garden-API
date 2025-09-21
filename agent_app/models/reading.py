from datetime import datetime
from pydantic import BaseModel


class ReadingDTO(BaseModel):
    id: int
    device_id: int
    value: str
    timestamp: datetime
    esp_id: int
