from typing import List, Sequence
from app.exceptions.scheme import AppException
from app.models.dtos.esp_device import EspDeviceDTO
from app.models.enums import ControlActionType, DeviceType
from app.models.dtos.devices import DeviceDTO
from app.mappers.devices import db_to_dto
from app.repos.devices import DeviceRepository
from app.core.mqtt.mqtt_publisher import MqttTopicPublisher


class DeviceService:
    def __init__(self, repo: DeviceRepository):
        self.repo = repo

    async def get_all_for_esps(self, esps: List[EspDeviceDTO]) -> List[DeviceDTO]:
        devices = await self.repo.get_all_for_esps(esps)
        return [db_to_dto(d) for d in devices]

    ACTUATORS = (DeviceType.ATOMIZER, DeviceType.FANNER,
                 DeviceType.HEATER, DeviceType.WATERER)

    async def create_all_for_esp(self, esp_id: int) -> List[DeviceDTO]:
        created_devices = []
        for device_type in DeviceType:
            enabled = None if device_type not in DeviceService.ACTUATORS else False
            created = await self.repo.create(
                esp_id=esp_id,
                type=device_type,
                enabled=enabled
            )
            created_devices.append(created)

        return [db_to_dto(d) for d in created_devices]

    async def control_device(
        self,
        esps: Sequence[EspDeviceDTO],
        type: DeviceType,
        action: ControlActionType,
    ) -> bool:
        devices = await self.repo.get_all_for_esps(esps)

        matching_devices = [
            device
            for device in devices
            if device.type == type and device.esp and device.esp.mac
        ]

        if not matching_devices:
            raise AppException(
                message=f"No devices of type {type} with MAC address found for given ESPs",
                status_code=404,
            )

        publisher = MqttTopicPublisher()

        for device in matching_devices:
            payload = {"action": {"id": int(action)}}
            await publisher.publish(
                topic=f"{device.esp.mac}/device/control",
                payload=payload,
            )

        return True
