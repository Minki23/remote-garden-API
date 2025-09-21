from pydantic import BaseModel


class TriggerDTO(BaseModel):
    refresh_token: str
    garden_id: int
