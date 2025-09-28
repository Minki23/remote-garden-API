from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AgentDTO(BaseModel):
    id: int
    garden_id: int
    enabled: bool
    refresh_expires_at: Optional[datetime]
    context: Optional[str]


class AgentEnableRequest(BaseModel):
    context: str | None = None
