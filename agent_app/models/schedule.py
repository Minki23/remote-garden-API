from pydantic import BaseModel
from models.enums import ScheduleActionType


class ScheduleDTO(BaseModel):
    """
    DTO representing a scheduled action with its cron expression.
    """
    action: ScheduleActionType
    cron: str
