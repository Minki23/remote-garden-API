from common_db.db import DeviceDb
from models.dtos.devices import DeviceDTO


def db_to_dto(device: DeviceDb) -> DeviceDTO:
    return DeviceDTO(
        id=device.id,
        type=device.type,
    )
