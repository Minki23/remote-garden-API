
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security.jwt import decode_access_token
from app.exceptions.scheme import AppException
import logging

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False) #@TODO change to True if you want to enforce authentication

async def _get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    return 1

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