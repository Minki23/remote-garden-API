from common_db.enums import ScheduleActionType
from pydantic import BaseModel
from typing import Literal, List


class WeeklyScheduleDTO(BaseModel):
    days_of_week: List[Literal["mon", "tue",
                               "wed", "thu", "fri", "sat", "sun"]]
    hour: int  # 0-23
    minute: int  # 0-59
    action: ScheduleActionType


class ScheduleCreateDTO(BaseModel):
    action: ScheduleActionType
    cron: str
