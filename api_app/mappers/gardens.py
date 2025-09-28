from common_db import db
from models.dtos import gardens as dto


def db_to_garden_dto(garden: db.GardenDb) -> dto.GardenDTO:
    """
    Convert a GardenDb ORM object to a GardenDTO.
    """
    return dto.GardenDTO(
        id=garden.id,
        user_id=garden.user_id,
        name=garden.name,
        created_at=garden.created_at,
        updated_at=garden.updated_at,
        send_notifications=garden.send_notifications,
        enable_automation=garden.enable_automation,
        use_fahrenheit=garden.use_fahrenheit,
    )
