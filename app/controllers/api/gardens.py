from fastapi import APIRouter
from app.core.config import CONFIG
from app.core.dependencies import GardenServiceDep, CurrentUserDep, GardenDep, AgentServiceDep, ScheduleServiceDep
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
    agent_service: AgentServiceDep,
    schedule_service: ScheduleServiceDep
):
    garden = await service.create_garden(dto, user_id)
    await agent_service.create_agent_for_garden(garden.id)
    schedule_service.create_agent(garden.id, CONFIG.AGENT_TRIGGER)
    return garden


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
    await service.delete_garden(garden.id)


@router.get("/", response_model=list[GardenDTO])
async def get_my_gardens(
    service: GardenServiceDep,
    user_id: CurrentUserDep,
):
    return await service.get_gardens_by_user(user_id)


@router.get("/{garden_id}", response_model=GardenDTO)
async def get_garden_by_id(
    garden: GardenDep,
):
    return garden


@router.patch("/{garden_id}/preferences", response_model=GardenDTO)
async def update_preferences(
    prefs: GardenPreferencesUpdateDTO,
    service: GardenServiceDep,
    garden: GardenDep,
) -> GardenDTO:
    return await service.update_preferences(garden.id, prefs)
