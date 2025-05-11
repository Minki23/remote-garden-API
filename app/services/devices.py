from models.dtos.devices import DeviceDTO, DeviceCreateDTO
from mappers.devices import db_to_dto
from repos.devices import DeviceRepository


class DeviceService:
    def __init__(self, repo: DeviceRepository):
        self.repo = repo

    async def get_all(self) -> list[DeviceDTO]:
        devices = await self.repo.get_all()
        return [db_to_dto(d) for d in devices]

    async def get_by_id(self, id: int) -> DeviceDTO:
        device = await self.repo.get_by_id(id)
        return db_to_dto(device)

    async def create(self, dto: DeviceCreateDTO) -> DeviceDTO:
        device = await self.repo.create(
            garden_id=dto.garden_id, mac=dto.mac, type=dto.device_type
        )
        return db_to_dto(device)

    async def delete(self, id: int) -> bool:
        return await self.repo.delete(id)

    async def get_all_for_garden(self, garden_id: int) -> list[DeviceDTO]:
        devices = await self.repo.get_all_by_garden_id(garden_id)
        return [db_to_dto(d) for d in devices]

    async def create_all_for_garden(
        self, garden_id: int, dtos: list[DeviceCreateDTO]
    ) -> list[DeviceDTO]:
        result = []
        for dto in dtos:
            device = await self.repo.create(
                garden_id=garden_id, mac=dto.mac, device_type=dto.device_type
            )
            result.append(db_to_dto(device))
        return result
