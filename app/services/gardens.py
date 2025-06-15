from typing import List
from app.core.mqtt.mqtt_publisher import MqttTopicPublisher
from app.models.dtos.devices import DeviceCreateDTO
from app.models.enums import DeviceType
from app.repos.gardens import GardenRepository
from app.services.devices import DeviceService
from app.models.dtos.gardens import (
    GardenConfigureDTO,
    GardenDTO,
    GardenCreateDTO,
    GardenPreferencesUpdateDTO,
)
from app.exceptions.scheme import AppException


class GardenService:
    def __init__(self, repo: GardenRepository, device_service: DeviceService):
        self.repo = repo
        self.device_service = device_service

    async def create_garden(self, dto: GardenCreateDTO, user_id: int) -> GardenDTO:
        garden = await self.repo.create(user_id=user_id, name=dto.name)
        garden_dto = GardenDTO(**garden.__dict__)

        device_dtos = [
            DeviceCreateDTO(
                garden_id=garden_dto.id,
                mac=f"{DeviceType.__name__}-{type.name}-{garden_dto.id}",
                type=type,
            )
            for type in DeviceType
        ]

        await self.device_service.create_all_for_garden(garden_dto.id, device_dtos)

        return garden_dto

    async def delete_garden(self, garden_id: int, user_id: int) -> None:
        await self.repo.delete(garden_id)

    async def update_garden_name(self, garden_id: int, name: str) -> GardenDTO:
        updated = await self.repo.update(garden_id, name=name)
        return GardenDTO(**updated.__dict__)

    async def get_gardens_by_user(self, user_id: int) -> List[GardenDTO]:
        gardens = await self.repo.get_all_by_user(user_id)
        return [GardenDTO(**g.__dict__) for g in gardens]

    async def configure_garden(self, garden_id: int, config: GardenConfigureDTO) -> bool:
        payload = {
            "ssid": config.ssid,
            "password": config.password
        }

        await MqttTopicPublisher().publish(f"device/{garden_id}/configure", payload)
        return True

    async def update_preferences(
        self, garden_id: int, prefs: GardenPreferencesUpdateDTO
    ) -> GardenDTO:
        updated = await self.repo.update(
            garden_id,
            send_notifications=prefs.send_notifications,
            enable_automation=prefs.enable_automation,
            use_fahrenheit=prefs.use_fahrenheit,
        )
        return GardenDTO(**updated.__dict__)
