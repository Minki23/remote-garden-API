from pydantic import BaseModel


class StatusDTO(BaseModel):
    battery_level: float  # %
    is_online: bool
    signal_strength: int  # dBm
    system_ok: bool
