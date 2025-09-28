from datetime import datetime
from pydantic import BaseModel


class ApiReadingDTO(BaseModel):
    """
    DTO representing a single sensor reading.
    """
    id: int
    device_id: int
    value: str
    timestamp: datetime
    esp_id: int
