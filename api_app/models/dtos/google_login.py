from pydantic import BaseModel


class GoogleLoginDTO(BaseModel):
    id_token: str
