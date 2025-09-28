from datetime import datetime, timedelta
from core.config import CONFIG
from exceptions.scheme import AppException
from repos.agents import AgentRepository
from core.security.jwt import (
    create_access_token_for_agent,
    create_refresh_token,
)
from models.dtos.auth import TokenDTO


class AgentService:
    """
    Service layer for managing garden agents.

    Handles agent lifecycle: creation, enabling/disabling, and
    issuing/refreshing JWT tokens for agent authentication.
    """

    def __init__(self, agent_repo: AgentRepository):
        """
        Initialize the service with a repository for agent persistence.
        """
        self.agent_repo = agent_repo

    async def create_agent_for_garden(self, garden_id: int) -> TokenDTO:
        """
        Create a new agent for the given garden and issue tokens.

        Raises
        ------
        AppException
            If an agent already exists for this garden.
        """
        existing = await self.agent_repo.get_by_garden(garden_id)
        if existing:
            raise AppException("Agent for this garden already exists", 400)

        agent = await self.agent_repo.create(garden_id=garden_id, enabled=True)

        access_token = create_access_token_for_agent(agent.id)
        refresh_token = create_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=CONFIG.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.agent_repo.save_refresh_token(agent.id, refresh_token, expires_at)

        return TokenDTO(access_token=access_token, refresh_token=refresh_token)

    async def enable_agent_for_garden(
        self,
        garden_id: int,
        context: str | None = None
    ) -> TokenDTO:
        """
        Enable an existing agent and issue new tokens.

        Raises
        ------
        AppException
            If no agent exists for the given garden.
        """
        agent = await self.agent_repo.get_by_garden(garden_id)
        if not agent:
            raise AppException("Agent not found for this garden", 404)

        agent = await self.agent_repo.update(
            agent.id,
            enabled=True,
            context=context
        )

        access_token = create_access_token_for_agent(agent.id)
        refresh_token = create_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=CONFIG.REFRESH_TOKEN_EXPIRE_DAYS)

        await self.agent_repo.save_refresh_token(agent.id, refresh_token, expires_at)

        return TokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def disable_agent_for_garden(self, garden_id: int) -> bool:
        """
        Disable the agent for a given garden.

        Raises
        ------
        AppException
            If no agent exists for the given garden.
        """
        agent = await self.agent_repo.get_by_garden(garden_id)
        if not agent:
            raise AppException("Agent not found for this garden", 404)

        await self.agent_repo.update(agent.id, enabled=False)
        return True

    async def refresh(self, refresh_token: str) -> TokenDTO:
        """
        Refresh the access token using a valid refresh token.

        Raises
        ------
        AppException
            If the refresh token is invalid or expired.
        """
        agent = await self.agent_repo.get_by_refresh_token(refresh_token)
        if not agent:
            raise AppException("Invalid refresh token", 401)

        if not agent.refresh_expires_at or agent.refresh_expires_at < datetime.utcnow():
            raise AppException("Refresh token expired", 401)

        access_token = create_access_token_for_agent(agent.id)
        return TokenDTO(access_token=access_token, refresh_token=refresh_token)
