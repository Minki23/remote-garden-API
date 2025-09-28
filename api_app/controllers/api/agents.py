from fastapi import APIRouter
from core.config import CONFIG
from models.dtos.auth import RefreshTokenDTO, TokenDTO
from models.dtos.agents import AgentEnableRequest
from core.dependencies import AgentServiceDep, GardenDep, ScheduleServiceDep

router = APIRouter()


@router.post("/enable/{garden_id}", response_model=TokenDTO)
async def enable_agent_for_garden(
    garden: GardenDep,
    agent_service: AgentServiceDep,
    schedule_service: ScheduleServiceDep,
    body: AgentEnableRequest
):
    """
    Enable the agent for a given garden.

    Activates the agent and schedules AI tasks.
    """
    enabler = await agent_service.enable_agent_for_garden(
        garden.id,
        context=body.context
    )
    schedule_service.set_enable(garden.id, True)
    return enabler


@router.post("/disable/{garden_id}")
async def disable_agent_for_garden(
    garden: GardenDep,
    agent_service: AgentServiceDep,
    schedule_service: ScheduleServiceDep
):
    """
    Disable the agent for a given garden.

    Deactivates the agent and clears scheduled AI tasks.
    """
    enabler = await agent_service.disable_agent_for_garden(garden.id)
    schedule_service.set_enable(garden.id, False)
    schedule_service.delete_all_ai(garden.id)
    return enabler


@router.post("/refresh", response_model=TokenDTO)
async def refresh_agent(
    dto: RefreshTokenDTO,
    agent_service: AgentServiceDep,
):
    """
    Refresh the agent token.
    """
    return await agent_service.refresh(dto.refresh_token)


@router.post("/create/{garden_id}", response_model=TokenDTO)
async def create_agent_for_garden(
    garden: GardenDep,
    agent_service: AgentServiceDep,
    schedule_service: ScheduleServiceDep
):
    """
    Create a new agent for a given garden.

    Registers the agent and sets up its schedule.
    """
    agent = await agent_service.create_agent_for_garden(garden.id)
    schedule_service.create_agent(garden.id, CONFIG.AGENT_TRIGGER)
    return agent
