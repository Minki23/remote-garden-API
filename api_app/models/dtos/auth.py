from pydantic import BaseModel


class TokenDTO(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class RefreshTokenDTO(BaseModel):
    refresh_token: str
