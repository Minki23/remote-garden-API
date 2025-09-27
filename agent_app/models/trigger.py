from pydantic import BaseModel


class TriggerDTO(BaseModel):
    """
    DTO representing a trigger request for the agent.
    """
    refresh_token: str
    garden_id: int
