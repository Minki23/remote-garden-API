from fastapi import APIRouter
from app.core.dependencies import ReadingServiceDep
from app.models.dtos.readings import ReadingCreateDTO, ReadingDTO

router = APIRouter()


@router.post("/", response_model=ReadingDTO)
async def create_reading(dto: ReadingCreateDTO, service: ReadingServiceDep):
    return await service.create(dto)


@router.get("/device/{device_id}", response_model=list[ReadingDTO])
async def get_by_device(device_id: int, service: ReadingServiceDep):
    return await service.get_by_device(device_id)
