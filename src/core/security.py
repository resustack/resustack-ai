"""Security utilities for JWT token verification."""

from typing import Any

from jose import JWTError, jwt

from src.core.config import settings


def verify_token(token: str) -> dict[str, Any] | None:
    """
    Verify JWT token from Gateway.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> str | None:
    """
    Extract user ID from JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID or None if invalid
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None
