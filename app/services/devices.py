from typing import List, Sequence
from app.exceptions.scheme import AppException
from app.models.db import DeviceDb, EspDeviceDb
from app.models.dtos.esp_device import EspDeviceDTO
from app.models.enums import ControlActionType, DeviceType
from app.models.dtos.devices import DeviceDTO
from app.mappers.devices import db_to_dto
from app.repos.devices import DeviceRepository
from sqlalchemy import select
from app.core.mqtt.mqtt_publisher import MqttTopicPublisher
from sqlalchemy.orm import selectinload


class DeviceService:
    def __init__(self, repo: DeviceRepository):
        self.repo = repo

    async def get_all(self) -> list[DeviceDTO]:
        devices = await self.repo.get_all()
        return [db_to_dto(d) for d in devices]

    async def get_by_id(self, id: int) -> DeviceDTO:
        device = await self.repo.get_by_id(id)
        return db_to_dto(device)

    async def delete(self, id: int) -> bool:
        return await self.repo.delete(id)

    async def get_all_for_esps(self, esps: List[EspDeviceDTO]) -> List[DeviceDTO]:
        devices = await self.repo.get_all_for_esps(esps)
        return [db_to_dto(d) for d in devices]

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
                topic=f"devices/{device.esp.mac}/control",
                payload=payload,
            )

        return True
