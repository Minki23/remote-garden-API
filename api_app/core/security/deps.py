from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.db_context import get_async_session
from core.security.jwt import decode_access_token
from exceptions.scheme import AppException
import logging

from common_db.db import UserDb, AgentDb
from repos.users import UserRepository
from sqlalchemy.future import select
from enum import Enum

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(
    auto_error=False
)  # @TODO change to True if you want to enforce authentication


class SubjectType(str, Enum):
    USER = "user"
    AGENT = "agent"


async def get_current_subject(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> tuple[int, SubjectType]:
    logger.info("Validating user credentials")
    logger.info(f"Received credentials: {credentials}")

    if not credentials:
        raise AppException(status_code=401, message="Missing credentials")

    token = credentials.credentials
    payload = decode_access_token(token)

    sub_id = payload.get("sub_id")
    sub_type = payload.get("sub_type")

    if sub_id is None:
        raise AppException(status_code=401, message="Invalid subject id")

    if sub_type not in ("user", "agent"):
        raise AppException(status_code=401, message="Invalid subject type")

    return int(sub_id), SubjectType(sub_type)


async def _get_current_user_id(
    subject=Depends(get_current_subject),
) -> int:
    sub_id, sub_type = subject
    if sub_type != SubjectType.USER:
        raise AppException(status_code=403, message="User access required")
    return sub_id


get_current_user_id = _get_current_user_id


async def _get_current_admin_user(
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_async_session),
) -> UserDb:
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)

    if not user or not user.admin:
        raise AppException(status_code=403, message="Admin access required")

    return user


get_current_admin_user = _get_current_admin_user


async def _get_current_agent(
    subject=Depends(get_current_subject),
    db=Depends(get_async_session),
) -> AgentDb:
    sub_id, sub_type = subject
    if sub_type != SubjectType.AGENT:
        raise AppException(status_code=403, message="Agent access required")

    result = await db.execute(select(AgentDb).where(AgentDb.id == sub_id))
    agent = result.scalars().first()
    if not agent:
        raise AppException(status_code=401, message="Agent not found")

    return agent


get_current_agent = _get_current_agent
