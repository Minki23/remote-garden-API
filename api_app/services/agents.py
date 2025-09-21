from datetime import datetime, timedelta
from typing import List
from core.config import CONFIG
from exceptions.scheme import AppException
from repos.agents import AgentRepository
from core.security.jwt import (
    create_access_token_for_agent,
    create_refresh_token,
    hash_refresh_token,
    verify_refresh_token,
)
from models.dtos.auth import TokenDTO
from models.dtos.agents import AgentDTO
from mappers.agents import db_to_dto as db_agent_to_dto


class AgentService:
    def __init__(self, agent_repo: AgentRepository):
        self.agent_repo = agent_repo

    async def create_agent_for_garden(self, garden_id: int) -> TokenDTO:
        existing = await self.agent_repo.get_by_garden(garden_id)
        if existing:
            raise AppException("Agent for this garden already exists", 400)

        agent = await self.agent_repo.create(garden_id=garden_id, enabled=True)

        access_token = create_access_token_for_agent(agent.id)
        refresh_token = create_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=CONFIG.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.agent_repo.save_refresh_token(agent.id, refresh_token, expires_at)

        return TokenDTO(access_token=access_token, refresh_token=refresh_token)

    async def enable_agent_for_garden(self, garden_id: int) -> TokenDTO:
        agent = await self.agent_repo.get_by_garden(garden_id)
        if not agent:
            raise AppException("Agent not found for this garden", 404)

        agent = await self.agent_repo.update(agent.id, enabled=True)

        access_token = create_access_token_for_agent(agent.id)
        refresh_token = create_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=CONFIG.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.agent_repo.save_refresh_token(agent.id, refresh_token, expires_at)

        return TokenDTO(access_token=access_token, refresh_token=refresh_token)

    async def disable_agent_for_garden(self, garden_id: int) -> bool:
        agent = await self.agent_repo.get_by_garden(garden_id)
        if not agent:
            raise AppException("Agent not found for this garden", 404)

        await self.agent_repo.update(agent.id, enabled=False)
        return True

    async def refresh(self, refresh_token: str) -> TokenDTO:
        agent = await self.agent_repo.get_by_refresh_token(refresh_token)
        if not agent:
            raise AppException("Invalid refresh token", 401)

        if not agent.refresh_expires_at or agent.refresh_expires_at < datetime.utcnow():
            raise AppException("Refresh token expired", 401)

        access_token = create_access_token_for_agent(agent.id)
        return TokenDTO(access_token=access_token, refresh_token=refresh_token)
