from app.models.enums import DeviceType
from fastapi import APIRouter
from app.core.dependencies import DeviceServiceDep
from app.models.dtos.devices import DeviceCreateDTO, DeviceDTO
from app.models.dtos.status import StatusDTO
from app.core.dependencies import StatusServiceDep

router = APIRouter()


@router.get("/{garden_id}", response_model=list[DeviceDTO])
async def get_by_garden(garden_id: int, service: DeviceServiceDep):
    return await service.get_all_for_garden(garden_id)

@router.get("/status", response_model=StatusDTO)
async def get_status(service: StatusServiceDep):
    return await service.get_status(DeviceType.ESP)