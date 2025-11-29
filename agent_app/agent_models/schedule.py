from pydantic import BaseModel
from typing import List, Optional, Union
from agent_models.enums import ScheduleActionType


class CronDTO(BaseModel):
    __type__: str
    minute: str
    hour: str
    day_of_week: str
    day_of_month: str
    month_of_year: str


class ApiScheduleDTO(BaseModel):
    task_id: str
    enabled: bool
    cron: CronDTO
    args: List[Union[int, str]]
    garden_id: int
    action: Optional[ScheduleActionType]
    task: str
    created_by_ai: bool
