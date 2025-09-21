from models.db import ReadingDb
from models.dtos.readings import ReadingDTO


def db_to_dto(reading: ReadingDb) -> ReadingDTO:
    return ReadingDTO(
        id=reading.id,
        device_id=reading.device_id,
        value=reading.value,
        timestamp=reading.timestamp,
        esp_id=reading.device.esp.id
    )
