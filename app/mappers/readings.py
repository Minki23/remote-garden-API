from app.models.db import ReadingDb
from app.models.dtos.readings import ReadingDTO


def db_to_dto(reading: ReadingDb) -> ReadingDTO:
    return ReadingDTO(
        id=reading.id,
        device_id=reading.device_id,
        value=reading.value,
        timestamp=reading.timestamp,
    )
