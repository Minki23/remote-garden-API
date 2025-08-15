from fastapi import APIRouter
from app.core.dependencies import GardenServiceDep, CurrentUserDep, GardenDep
from app.models.dtos.gardens import (
    GardenCreateDTO,
    GardenDTO,
    GardenPreferencesUpdateDTO,
    GardenUpdateDTO,
)

router = APIRouter()


@router.post("/", response_model=GardenDTO)
async def create_garden(
    dto: GardenCreateDTO,
    service: GardenServiceDep,
    user_id: CurrentUserDep,
):
    return await service.create_garden(dto, user_id)


@router.put("/{garden_id}", response_model=GardenDTO)
async def update_name(
    dto: GardenUpdateDTO,
    service: GardenServiceDep,
    garden: GardenDep,
):
    return await service.update_garden_name(garden.id, dto.name)


@router.delete("/{garden_id}")
async def delete_garden(
    service: GardenServiceDep,
    garden: GardenDep,
):
    await service.delete_garden(garden.id, garden.user_id)


@router.get("/", response_model=list[GardenDTO])
async def get_my_gardens(
    service: GardenServiceDep,
    user_id: CurrentUserDep,
):
    return await service.get_gardens_by_user(user_id)


@router.patch("/{garden_id}/preferences", response_model=GardenDTO)
async def update_preferences(
    prefs: GardenPreferencesUpdateDTO,
    service: GardenServiceDep,
    garden: GardenDep,
) -> GardenDTO:
    return await service.update_preferences(garden.id, prefs)
