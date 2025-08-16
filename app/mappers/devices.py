from app.models.db import DeviceDb
from app.models.dtos.devices import DeviceDTO


def db_to_dto(device: DeviceDb) -> DeviceDTO:
    return DeviceDTO(
        id=device.id,
        type=device.type,
    )
