from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from core.dependencies import (
    ReadingServiceDep,
    GardenDep,
)
from models.dtos.readings import ReadingDTO
from models.enums import DeviceType

router = APIRouter()


@router.get("/garden/{garden_id}/device-type/{type}", response_model=list[ReadingDTO])
async def get_by_filters_for_garden_paginated(
    garden: GardenDep,
    type: DeviceType,
    service: ReadingServiceDep,
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, gt=0),
):
    start_time = start_time or datetime.min
    end_time = end_time or datetime.utcnow()

    return await service.get_by_garden_filters_paginated(
        garden_id=garden.id,
        type=type,
        start_time=start_time,
        end_time=end_time,
        offset=offset,
        limit=limit,
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
