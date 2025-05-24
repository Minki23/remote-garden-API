from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from app.core.dependencies import CurrentUserDep, ReadingServiceDep, GardenDep, UserDeviceDep
from app.models.dtos.readings import ReadingDTO
from app.models.enums import DeviceType

router = APIRouter()


@router.get("/device/{device_id}", response_model=list[ReadingDTO])
async def get_by_device(
    device: UserDeviceDep,
    service: ReadingServiceDep,
):
    return await service.get_by_device(device.id)


@router.get("/garden/{garden_id}/filter", response_model=list[ReadingDTO])
async def get_by_filters_for_garden(
    garden: GardenDep,
    type: DeviceType,
    service: ReadingServiceDep,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    start_time = start_time or datetime.min
    end_time = end_time or datetime.utcnow()

    return await service.get_by_garden_filters(
        garden_id=garden.id,
        type=type,
        start_time=start_time,
        end_time=end_time,
    )


@router.get("/garden/{garden_id}/device-type/{type}/last", response_model=ReadingDTO)
async def get_last_by_device_type(
    garden: GardenDep,
    type: DeviceType,
    service: ReadingServiceDep,
):
    return await service.get_last_for_garden_device_type(
        garden_id=garden.id,
        type=type,
    )

