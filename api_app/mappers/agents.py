from models.db import AgentDb
from models.dtos.agents import AgentDTO


def db_to_dto(agent: AgentDb) -> AgentDTO:
    return AgentDTO(
        id=agent.id,
        garden_id=agent.garden_id,
        enabled=agent.enabled,
        refresh_expires_at=agent.refresh_expires_at,
    )
