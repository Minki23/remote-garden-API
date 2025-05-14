from fastapi import APIRouter
from app.core.dependencies import GardenServiceDep, CurrentUserDep
from app.models.dtos.gardens import GardenCreateDTO, GardenDTO, GardenPreferencesUpdateDTO, GardenUpdateDTO
from app.models.dtos.gardens import GardenConfigureDTO
router = APIRouter()


@router.post("/", response_model=GardenDTO)
async def create_garden(dto: GardenCreateDTO, service: GardenServiceDep, user_id: CurrentUserDep):
    return await service.create_garden(dto, user_id)


@router.put("/{garden_id}", response_model=GardenDTO)
async def update_name(
    garden_id: int, dto: GardenUpdateDTO, service: GardenServiceDep, user_id: CurrentUserDep
):
    return await service.update_garden_name(garden_id, dto.name, user_id)


@router.delete("/{garden_id}")
async def delete_garden(garden_id: int, service: GardenServiceDep, user_id: CurrentUserDep):
    await service.delete_garden(garden_id, user_id)


@router.get("/", response_model=list[GardenDTO])
async def get_my_gardens(service: GardenServiceDep, user_id: CurrentUserDep):
    return await service.get_gardens_by_user(user_id)


@router.post("/{garden_id}/configure", response_model=bool)
async def configure_garden(
    garden_id: int,
    config: GardenConfigureDTO,
    service: GardenServiceDep,
    user_id: CurrentUserDep
) -> bool:
    return await service.configure_garden(garden_id, user_id, config)

@router.patch("/{garden_id}/preferences", response_model=GardenDTO)
async def update_preferences(
    garden_id: int,
    prefs: GardenPreferencesUpdateDTO,
    service: GardenServiceDep,
    user_id: CurrentUserDep
) -> GardenDTO:
    return await service.update_preferences(garden_id, user_id, prefs)