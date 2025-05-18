from app.models.db import DeviceDb
from app.models.dtos.devices import DeviceDTO, DeviceCreateDTO


def db_to_dto(device: DeviceDb) -> DeviceDTO:
    return DeviceDTO(
        id=device.id,
        garden_id=device.garden_id,
        mac=device.mac,
        type=device.type,
        created_at=device.created_at,
        updated_at=device.updated_at,
    )
