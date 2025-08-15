from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EspDeviceDTO(BaseModel):
    id: int
    mac: str
    secret: str
    client_key: Optional[str]
    client_crt: Optional[str]
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime
    garden_id: Optional[int]
