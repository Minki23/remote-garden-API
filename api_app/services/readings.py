from exceptions.scheme import AppException
from models.dtos.readings import ReadingCreateDTO, ReadingDTO
from mappers.readings import db_to_dto
from repos.readings import ReadingRepository
from datetime import datetime
from models.enums import DeviceType


class ReadingService:
    def __init__(self, repo: ReadingRepository):
        self.repo = repo

    async def create(self, dto: ReadingCreateDTO) -> ReadingDTO:
        reading = await self.repo.create(device_id=dto.device_id, value=dto.value)
        return db_to_dto(reading)

    async def get_last_for_garden_device_type(
        self,
        garden_id: int,
        type: DeviceType,
    ) -> ReadingDTO:
        reading = await self.repo.get_last_for_garden_device_type(garden_id, type)
        if not reading:
            raise AppException("No reading found for device type", 404)

        return db_to_dto(reading)

    async def get_by_garden_filters_paginated(
        self,
        garden_id: int,
        type: DeviceType,
        start_time: datetime,
        end_time: datetime,
        offset: int,
        limit: int,
    ) -> list[ReadingDTO]:
        readings = await self.repo.get_by_garden_filters_paginated(
            garden_id, type, start_time, end_time, offset, limit
        )
        return [db_to_dto(r) for r in readings]
