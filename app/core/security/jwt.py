from datetime import datetime, timedelta
import hashlib
import hmac
import secrets
from jose import jwt
from app.core.config import CONFIG


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, CONFIG.SECRET_KEY, algorithm=CONFIG.ALGORITHM)


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def decode_access_token(token: str) -> dict:
    from jose import JWTError

    try:
        return jwt.decode(token, CONFIG.SECRET_KEY, algorithms=[CONFIG.ALGORITHM])
    except JWTError:
        return {}


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_refresh_token(token: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_refresh_token(token), hashed)
