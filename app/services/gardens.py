from typing import List
from app.repos.gardens import GardenRepository
from models.dtos.gardens import GardenConfigureDTO, GardenDTO, GardenCreateDTO, GardenPreferencesUpdateDTO
from exceptions.scheme import AppException


class GardenService:
    def __init__(self, repo: GardenRepository):
        self.repo = repo

    async def create_garden(self, dto: GardenCreateDTO, user_id: int) -> GardenDTO:
        garden = await self.repo.create(user_id=user_id, name=dto.name)
        return GardenDTO(**garden.__dict__)

    async def delete_garden(self, garden_id: int, user_id: int) -> None:
        garden = await self.repo.get_by_id_and_user(garden_id, user_id)
        if not garden:
            raise AppException(message="Garden not found or access denied", status_code=404)

        await self.repo.delete(garden_id)

    async def update_garden_name(self, garden_id: int, name: str, user_id: int) -> GardenDTO:
        garden = await self.repo.get_by_id_and_user(garden_id, user_id)
        if not garden:
            raise AppException(message="Garden not found or access denied", status_code=404)

        updated = await self.repo.update(garden_id, name=name)
        return GardenDTO(**updated.__dict__)

    async def get_gardens_by_user(self, user_id: int) -> List[GardenDTO]:
        gardens = await self.repo.get_all_by_user(user_id)
        return [GardenDTO(**g.__dict__) for g in gardens]

    async def configure_garden(
        self, garden_id: int, user_id: int, config: GardenConfigureDTO
    ) -> bool:
        garden = await self.repo.get_by_id_and_user(garden_id, user_id)
        if not garden:
            raise AppException("Garden not found or access denied", 404)

        # MOCK MQTT communication
        print(f"[MOCK MQTT] Sending SSID={config.ssid}, PASS={config.password} to garden {garden_id}")

        return True

    async def update_preferences(
        self,
        garden_id: int,
        user_id: int,
        prefs: GardenPreferencesUpdateDTO
    ) -> GardenDTO:
        garden = await self.repo.get_by_id_and_user(garden_id, user_id)
        if not garden:
            raise AppException("Garden not found or access denied", 404)

        updated = await self.repo.update(
            garden_id,
            send_notifications=prefs.send_notifications,
            enable_automation=prefs.enable_automation,
            use_fahrenheit=prefs.use_fahrenheit,
        )
        return GardenDTO(**updated.__dict__)