from typing import Optional
from pydantic import BaseModel


class RegisterDeviceDTO(BaseModel):
    fcm_token: str
    platform: Optional[str] = None


class RemoveDeviceDTO(BaseModel):
    fcm_token: str
