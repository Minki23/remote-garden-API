from app.exceptions.scheme import AppException
from app.repos.gardens import GardenRepository
from models.dtos.readings import ReadingDTO, ReadingCreateDTO
from mappers.readings import db_to_dto
from repos.readings import ReadingRepository
from datetime import datetime
from models.enums import DeviceType


class ReadingService:
    def __init__(self, repo: ReadingRepository):
        self.repo = repo

    async def get_all(self) -> list[ReadingDTO]:
        readings = await self.repo.get_all()
        return [db_to_dto(r) for r in readings]

    async def get_by_id(self, id: int) -> ReadingDTO:
        reading = await self.repo.get_by_id(id)
        return db_to_dto(reading)

    async def create(self, dto: ReadingCreateDTO) -> ReadingDTO:
        reading = await self.repo.create(device_id=dto.device_id, value=dto.value)
        return db_to_dto(reading)

    async def delete(self, id: int) -> bool:
        return await self.repo.delete(id)

    async def get_by_device(self, device_id: int) -> list[ReadingDTO]:
        readings = await self.repo.get_by_device(device_id)
        return [db_to_dto(r) for r in readings]

    async def get_by_garden_filters(
        self,
        garden_id: int,
        user_id: int,
        device_type: DeviceType,
        start_time: datetime,
        end_time: datetime,
    ) -> list[ReadingDTO]:
        garden = await GardenRepository(self.repo.db).get_by_id_and_user(garden_id, user_id)
        if not garden:
            raise AppException("Garden not found or access denied", 404)

        readings = await self.repo.get_by_garden_filters(
            garden_id, device_type, start_time, end_time
        )
        return [db_to_dto(r) for r in readings]

    async def get_last_for_garden_device_type(
        self, garden_id: int, device_type: DeviceType, user_id: int
    ) -> ReadingDTO:
        from app.repos.gardens import GardenRepository

        garden = await GardenRepository(self.repo.db).get_by_id_and_user(garden_id, user_id)
        if not garden:
            raise AppException("Garden not found or access denied", 404)

        reading = await self.repo.get_last_for_garden_device_type(garden_id, device_type)
        if not reading:
            raise AppException("No reading found for device type", 404)

        return db_to_dto(reading)
