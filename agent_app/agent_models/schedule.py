from pydantic import BaseModel
from agent_models.enums import ScheduleActionType


class ApiScheduleDTO(BaseModel):
    """
    DTO representing a scheduled action with its cron expression.
    """
    action: ScheduleActionType
    cron: str
