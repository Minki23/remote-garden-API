from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreateDTO(BaseModel):
    email: EmailStr


class UserDTO(BaseModel):
    id: int
    email: EmailStr
    admin: bool
    created_at: datetime
    updated_at: datetime
