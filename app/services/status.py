from app.models.enums import DeviceType
from models.dtos.status import StatusDTO

class StatusService:
    async def get_status(self, device_type: DeviceType) -> StatusDTO:
        # ESP will be different device type that will be stored in db
        #@TODO insert mock of server
        print(f"[MOCK MQTT] Requesting status from device {device_type}")
        return StatusDTO(
            battery_level=83.5,
            is_online=True,
            signal_strength=-62,
            system_ok=True,
        )
