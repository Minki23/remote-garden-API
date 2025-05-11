from fastapi import APIRouter
from app.core.dependencies import DeviceServiceDep
from app.models.dtos.devices import DeviceCreateDTO, DeviceDTO

router = APIRouter()


@router.get("/{garden_id}", response_model=list[DeviceDTO])
async def get_by_garden(garden_id: int, service: DeviceServiceDep):
    return await service.get_all_for_garden(garden_id)
