from exceptions.scheme import AppException
from models.dtos.readings import ReadingCreateDTO, ReadingDTO
from mappers.readings import db_to_dto
from repos.readings import ReadingRepository
from datetime import datetime
from common_db.enums import DeviceType


class ReadingService:
    """
    Service for creating and retrieving sensor/device readings.
    """

    def __init__(self, repo: ReadingRepository):
        """
        Initialize the service with a reading repository.
        """
        self.repo = repo

    async def create(self, dto: ReadingCreateDTO) -> ReadingDTO:
        """
        Create a new reading for a given device.

        Parameters
        ----------
        dto : ReadingCreateDTO
            DTO with device ID and reading value.

        Returns
        -------
        ReadingDTO
            The created reading mapped to a DTO.
        """
        reading = await self.repo.create(device_id=dto.device_id, value=dto.value)
        return db_to_dto(reading)

    async def get_last_for_garden_device_type(
        self,
        garden_id: int,
        type: DeviceType,
    ) -> ReadingDTO:
        """
        Get the most recent reading for a device type in a specific garden.

        Parameters
        ----------
        garden_id : int
            ID of the garden.
        type : DeviceType
            Type of the device (e.g. HEATER, WATERER).

        Returns
        -------
        ReadingDTO
            The latest reading as DTO.

        Raises
        ------
        AppException
            If no reading is found for the given device type.
        """
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
        """
        Get readings for a device type in a garden within a time range (paginated).

        Parameters
        ----------
        garden_id : int
            ID of the garden.
        type : DeviceType
            Type of device.
        start_time : datetime
            Start of the time range.
        end_time : datetime
            End of the time range.
        offset : int
            Number of results to skip.
        limit : int
            Maximum number of results to return.

        Returns
        -------
        list[ReadingDTO]
            List of readings as DTOs.
        """
        readings = await self.repo.get_by_garden_filters_paginated(
            garden_id, type, start_time, end_time, offset, limit
        )
        return [db_to_dto(r) for r in readings]
