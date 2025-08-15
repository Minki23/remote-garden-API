from pydantic import BaseModel


class CreateEspDeviceRequest(BaseModel):
    mac: str
    secret: str
