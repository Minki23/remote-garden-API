from common_db.db import AgentDb
from models.dtos.agents import AgentDTO


def db_to_dto(agent: AgentDb) -> AgentDTO:
    """
    Convert an AgentDb ORM object to an AgentDTO.
    """
    return AgentDTO(
        id=agent.id,
        garden_id=agent.garden_id,
        enabled=agent.enabled,
        refresh_expires_at=agent.refresh_expires_at,
    )
