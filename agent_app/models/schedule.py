from pydantic import BaseModel
from models.enums import ScheduleActionType


class ScheduleDTO(BaseModel):
    action: ScheduleActionType
    cron: str
