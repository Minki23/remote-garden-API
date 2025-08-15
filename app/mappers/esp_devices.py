from app.models.dtos.esp_device import EspDeviceDTO
from app.models.db import EspDeviceDb


def db_esp_to_dto(db_obj: EspDeviceDb) -> EspDeviceDTO:
    return EspDeviceDTO(
        id=db_obj.id,
        mac=db_obj.mac,
        secret=db_obj.secret,
        client_key=db_obj.client_key,
        client_crt=db_obj.client_crt,
        last_seen_at=db_obj.last_seen_at,
        created_at=db_obj.created_at,
        updated_at=db_obj.updated_at,
        garden_id=db_obj.garden_id,
    )
