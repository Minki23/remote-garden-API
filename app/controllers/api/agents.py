from fastapi import APIRouter
from app.core.config import CONFIG
from app.models.dtos.auth import TokenDTO
from app.core.dependencies import AgentServiceDep, GardenDep, ScheduleServiceDep

router = APIRouter()


@router.post("/enable/{garden_id}", response_model=TokenDTO)
async def enable_agent_for_garden(
    garden: GardenDep,
    agent_service: AgentServiceDep,
    schedule_service: ScheduleServiceDep

):
    enabler = await agent_service.enable_agent_for_garden(garden.id)
    schedule_service.set_enable(garden.id, True)
    return enabler


@router.post("/disable/{garden_id}")
async def disable_agent_for_garden(
    garden: GardenDep,
    agent_service: AgentServiceDep,
    schedule_service: ScheduleServiceDep
):
    enabler = await agent_service.disable_agent_for_garden(garden.id)
    schedule_service.set_enable(garden.id, False)
    schedule_service.delete_all_ai(garden.id)
    return enabler


@router.post("/refresh", response_model=TokenDTO)
async def refresh_agent(
    refresh_token: str,
    agent_service: AgentServiceDep,
):
    return await agent_service.refresh(refresh_token)


@router.post("/create/{garden_id}", response_model=TokenDTO)
async def create_agent_for_garden(
    garden: GardenDep,
    agent_service: AgentServiceDep,
    schedule_service: ScheduleServiceDep
):
    agent = await agent_service.create_agent_for_garden(garden.id)
    schedule_service.create_agent(garden.id, CONFIG.AGENT_TRIGGER)
    return agent
