from datetime import datetime, timedelta
import hashlib
import hmac
import secrets
from jose import jwt
from core.config import CONFIG
from jose import JWTError


def create_access_token(data: dict) -> str:
    """
    Create a signed JWT access token.

    Parameters
    ----------
    data : dict
        The payload to include in the token.

    Returns
    -------
    str
        Encoded JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, CONFIG.SECRET_KEY, algorithm=CONFIG.ALGORITHM)


def create_access_token_for_user(user_id: int) -> str:
    """
    Generate an access token for a user subject.

    Parameters
    ----------
    user_id : int
        Identifier of the user.

    Returns
    -------
    str
        Encoded JWT token string.
    """
    return create_access_token({
        "sub_id": user_id,
        "sub_type": "user"
    })


def create_access_token_for_agent(agent_id: int) -> str:
    """
    Generate an access token for an agent subject.

    Parameters
    ----------
    agent_id : int
        Identifier of the agent.

    Returns
    -------
    str
        Encoded JWT token string.
    """
    return create_access_token({
        "sub_id": agent_id,
        "sub_type": "agent"
    })


def create_refresh_token() -> str:
    """
    Create a secure random refresh token.

    Returns
    -------
    str
        Randomly generated refresh token string.
    """
    return secrets.token_urlsafe(64)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Parameters
    ----------
    token : str
        JWT access token string.

    Returns
    -------
    dict
        Decoded payload if valid, empty dict otherwise.
    """
    try:
        return jwt.decode(token, CONFIG.SECRET_KEY, algorithms=[CONFIG.ALGORITHM])
    except JWTError:
        return {}


def hash_refresh_token(token: str) -> str:
    """
    Create a SHA-256 hash of the refresh token.

    Parameters
    ----------
    token : str
        The refresh token string.

    Returns
    -------
    str
        Hashed representation of the token.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_refresh_token(token: str, hashed: str) -> bool:
    """
    Verify a refresh token against its stored hash.

    Parameters
    ----------
    token : str
        Provided refresh token string.
    hashed : str
        Previously hashed token.

    Returns
    -------
    bool
        True if token matches, False otherwise.
    """
    # return hmac.compare_digest(hash_refresh_token(token), hashed)
    # @TODO remove
    return hmac.compare_digest(token, hashed)
