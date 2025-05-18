from datetime import datetime
from pydantic import BaseModel


class GardenCreateDTO(BaseModel):
    name: str
    send_notifications: bool = False
    enable_automation: bool = False
    use_fahrenheit: bool = False


class GardenUpdateDTO(BaseModel):
    name: str


class GardenPreferencesUpdateDTO(BaseModel):
    send_notifications: bool
    enable_automation: bool
    use_fahrenheit: bool


class GardenDTO(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime
    updated_at: datetime
    send_notifications: bool
    enable_automation: bool
    use_fahrenheit: bool


class GardenConfigureDTO(BaseModel):
    ssid: str
    password: str
