from datetime import datetime, timedelta
import hashlib
import hmac
import secrets
from jose import jwt
from core.config import CONFIG
from jose import JWTError


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, CONFIG.SECRET_KEY, algorithm=CONFIG.ALGORITHM)


def create_access_token_for_user(user_id: int) -> str:
    return create_access_token({
        "sub_id": user_id,
        "sub_type": "user"
    })


def create_access_token_for_agent(agent_id: int) -> str:
    return create_access_token({
        "sub_id": agent_id,
        "sub_type": "agent"
    })


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, CONFIG.SECRET_KEY, algorithms=[CONFIG.ALGORITHM])
    except JWTError:
        return {}


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_refresh_token(token: str, hashed: str) -> bool:
    # return hmac.compare_digest(hash_refresh_token(token), hashed)
    # @TODO remove
    return hmac.compare_digest(token, hashed)
