from app.models.enums import DeviceType
from app.models.dtos.status import StatusDTO


class StatusService:
    async def get_status(self, type: DeviceType, garden_id: str) -> StatusDTO:
        # ESP will be different device type that will be stored in db
        # @TODO insert mock of server
        print(f"[MOCK MQTT] Requesting status from device {type}")
        return StatusDTO(
            battery_level=83.5,
            is_online=True,
            signal_strength=-62,
            system_ok=True,
        )
