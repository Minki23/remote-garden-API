from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from common_db.db import AgentDb
from .utils.super_repo import SuperRepo
from datetime import datetime


class AgentRepository(SuperRepo[AgentDb]):
    """
    Repository for managing `AgentDb` entities.
    Extends the generic SuperRepo with agent-specific queries.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db, AgentDb)

    async def get_by_garden(self, garden_id: int) -> Optional[AgentDb]:
        """
        Fetch the agent assigned to a specific garden.
        Returns None if no agent exists.
        """
        result = await self.db.execute(
            select(self.model).where(self.model.garden_id == garden_id)
        )
        return result.scalar_one_or_none()

    async def get_enabled(self, garden_id: int) -> Optional[AgentDb]:
        """
        Fetch the agent for a garden if it is currently enabled.
        Returns None if disabled or missing.
        """
        result = await self.db.execute(
            select(self.model).where(
                self.model.garden_id == garden_id, self.model.enabled == True
            )
        )
        return result.scalar_one_or_none()

    async def save_refresh_token(
        self, agent_id: int, token_hash: str, expires_at: datetime
    ) -> Optional[AgentDb]:
        """
        Store a new refresh token hash and expiration for the agent.
        Returns updated agent or None if not found.
        """
        agent = await self.get_by_id(agent_id)
        if not agent:
            return None
        agent.refresh_token_hash = token_hash
        agent.refresh_expires_at = expires_at
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def get_by_refresh_token(self, token_hash: str) -> Optional[AgentDb]:
        """
        Find an agent by its refresh token hash.
        Returns None if no match exists.
        """
        result = await self.db.execute(
            select(self.model).where(
                self.model.refresh_token_hash == token_hash)
        )
        return result.scalar_one_or_none()
