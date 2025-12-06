from common_db.db import DeviceDb
from common_db.enums import DeviceType
from models.dtos.devices import DeviceDTO

# Actuator device types
ACTUATOR_TYPES = {
    DeviceType.WATERER,
    DeviceType.ATOMIZER,
    DeviceType.FANNER,
    DeviceType.HEATER,
}


def db_to_dto(device: DeviceDb) -> DeviceDTO:
    """
    Convert a DeviceDb ORM object to a DeviceDTO.
    
    Status calculation:
    - For actuators: uses the device's 'enabled' field (updated from MQTT confirm messages)
    - For sensors: uses the ESP device's 'status' field (whether ESP is running)
    """
    # Determine status based on device type
    if device.type in ACTUATOR_TYPES:
        # Actuators: use device.enabled (from MQTT confirm)
        status = device.enabled
    else:
        # Sensors: use ESP status (whether ESP is stopped or resumed)
        status = device.esp.status if device.esp else None
    
    return DeviceDTO(
        id=device.id,
        type=device.type,
        status=status,
    )
