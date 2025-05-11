from models import db
from models.dtos import gardens as dto


def db_to_garden_dto(garden: db.GardenDb) -> dto.GardenDTO:
    return dto.GardenDTO(
        id=garden.id,
        name=garden.name,
        created_at=garden.created_at,
        updated_at=garden.updated_at,
    )
