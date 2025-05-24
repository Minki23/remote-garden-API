from pydantic import BaseModel

class TokenDTO(BaseModel):
    access_token: str
