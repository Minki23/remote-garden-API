from datetime import datetime
from pydantic import BaseModel


class GardenCreateDTO(BaseModel):
    name: str


class GardenUpdateDTO(BaseModel):
    name: str


class GardenDTO(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime
    updated_at: datetime
