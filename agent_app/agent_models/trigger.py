from pydantic import BaseModel


class ApiTriggerDTO(BaseModel):
    """
    DTO representing a trigger request for the agent.
    """
    refresh_token: str
    garden_id: int
    context: str
