from models.dtos.readings import ReadingDTO, ReadingCreateDTO
from mappers.readings import db_to_dto
from repos.readings import ReadingRepository


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
