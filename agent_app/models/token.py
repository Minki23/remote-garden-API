from pydantic import BaseModel


class TokenDTO(BaseModel):
    """
    DTO representing authentication tokens.
    """
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
