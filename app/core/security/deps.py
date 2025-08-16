from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.db_context import get_async_session
from app.core.security.jwt import decode_access_token
from app.exceptions.scheme import AppException
import logging

from app.models.db import UserDb
from app.repos.users import UserRepository

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(
    auto_error=False
)  # @TODO change to True if you want to enforce authentication


async def _get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    logger.info("Validating user credentials")
    logger.info(f"Received credentials: {credentials}")

    if not credentials:
        raise AppException(status_code=401, message="Missing credentials")

    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise AppException(status_code=401, message="Invalid token")

    return int(user_id)


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
