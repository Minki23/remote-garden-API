from pydantic import BaseModel
from models.enums import DeviceType


class DeviceDTO(BaseModel):
    """
    Data Transfer Object representing a device.

    Attributes
    ----------
    id : int
        Unique identifier of the device.
    type : DeviceType
        Type of the device (e.g., WATERER, ATOMIZER, etc.).
    """

    id: int
    type: DeviceType
