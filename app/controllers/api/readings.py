from fastapi import APIRouter, Depends, Query
from app.core.dependencies import CurrentUserDep, ReadingServiceDep
from app.models.dtos.readings import ReadingCreateDTO, ReadingDTO
from fastapi import Query
from datetime import datetime
from models.enums import DeviceType
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from typing import Optional


router = APIRouter()


# @router.post("/", response_model=ReadingDTO)
# async def create_reading(dto: ReadingCreateDTO, service: ReadingServiceDep):
#     return await service.create(dto)


@router.get("/device/{device_id}", response_model=list[ReadingDTO])
async def get_by_device(device_id: int, service: ReadingServiceDep):
    return await service.get_by_device(device_id)

@router.get("/garden/{garden_id}/filter", response_model=list[ReadingDTO])
async def get_by_filters_for_garden(
    garden_id: int,
    device_type: DeviceType,
    service: ReadingServiceDep,
    user_id: CurrentUserDep,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    start_time = start_time or datetime.min
    end_time = end_time or datetime.utcnow()
    return await service.get_by_garden_filters(
        garden_id, user_id, device_type, start_time, end_time
    )


@router.get("/garden/{garden_id}/device-type/{device_type}/last", response_model=ReadingDTO)
async def get_last_by_device_type(
    garden_id: int,
    device_type: DeviceType,
    service: ReadingServiceDep,
    user_id: CurrentUserDep
):
    return await service.get_last_for_garden_device_type(garden_id, device_type, user_id)
