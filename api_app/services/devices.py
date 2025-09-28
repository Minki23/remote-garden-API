from typing import List, Sequence
from exceptions.scheme import AppException
from models.dtos.esp_device import EspDeviceDTO
from common_db.enums import ControlActionType, DeviceType
from models.dtos.devices import DeviceDTO
from mappers.devices import db_to_dto
from repos.devices import DeviceRepository
from core.mqtt.mqtt_publisher import MqttTopicPublisher


class DeviceService:
    """
    Service for managing devices and sending control actions via MQTT.
    """

    ACTUATORS = (
        DeviceType.ATOMIZER,
        DeviceType.FANNER,
        DeviceType.HEATER,
        DeviceType.WATERER,
    )

    def __init__(self, repo: DeviceRepository):
        """
        Initialize the service with a device repository.
        """
        self.repo = repo

    async def get_all_for_esps(self, esps: List[EspDeviceDTO]) -> List[DeviceDTO]:
        """
        Retrieve all devices for the given ESPs.

        Parameters
        ----------
        esps : List[EspDeviceDTO]
            List of ESP device DTOs.

        Returns
        -------
        List[DeviceDTO]
            List of devices mapped to DTOs.
        """
        devices = await self.repo.get_all_for_esps(esps)
        return [db_to_dto(d) for d in devices]

    async def create_all_for_esp(self, esp_id: int) -> List[DeviceDTO]:
        """
        Create default devices for a newly registered ESP.

        Actuator devices are created with `enabled=False` by default.

        Parameters
        ----------
        esp_id : int
            The ID of the ESP device.

        Returns
        -------
        List[DeviceDTO]
            List of created devices as DTOs.
        """
        created_devices = []
        for device_type in DeviceType:
            enabled = None if device_type not in DeviceService.ACTUATORS else False
            created = await self.repo.create(
                esp_id=esp_id,
                type=device_type,
                enabled=enabled,
            )
            created_devices.append(created)

        return [db_to_dto(d) for d in created_devices]

    async def control_device(
        self,
        esps: Sequence[EspDeviceDTO],
        type: DeviceType,
        action: ControlActionType,
    ) -> bool:
        """
        Send a control command for devices of a given type through MQTT.

        Parameters
        ----------
        esps : Sequence[EspDeviceDTO]
            ESP devices where the target devices are registered.
        type : DeviceType
            Type of device to control (e.g. WATERER, HEATER).
        action : ControlActionType
            Control action to perform (e.g. WATER_ON, FAN_OFF).

        Returns
        -------
        bool
            True if messages were successfully published.

        Raises
        ------
        AppException
            If no matching devices are found for the given ESPs.
        """
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
            payload = {"action": {"id": action.value}}
            await publisher.publish(
                topic=f"{device.esp.mac}/device/control",
                payload=payload,
            )

        return True
