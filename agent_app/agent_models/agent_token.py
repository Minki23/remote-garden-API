from pydantic import BaseModel


class AgentTokenDTO(BaseModel):
    """
    DTO representing agent authentication tokens.
    """
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
