"""JWT access-token helpers."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError


JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 8


def get_jwt_secret_key() -> str:
    """Return the required JWT signing key.

    Returns:
        JWT signing key from the environment.

    Raises:
        RuntimeError: If JWT_SECRET_KEY is not configured.
    """
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY must be configured")
    return secret_key


def create_access_token(user_id: int, username: str) -> str:
    """Create an eight-hour JWT for an authenticated user.

    Args:
        user_id: Authenticated user identifier.
        username: Authenticated user login name.

    Returns:
        Signed JWT bearer token.
    """
    expires_at = datetime.now(UTC) + timedelta(hours=JWT_EXPIRATION_HOURS)
    return jwt.encode(
        {"sub": str(user_id), "username": username, "exp": expires_at},
        get_jwt_secret_key(),
        algorithm=JWT_ALGORITHM,
    )


def verify_access_token(token: str) -> int | None:
    """Return the token subject when a JWT is valid.

    Args:
        token: JWT bearer token to verify.

    Returns:
        Authenticated user identifier, or None for an invalid token.
    """
    try:
        payload = jwt.decode(token, get_jwt_secret_key(), algorithms=[JWT_ALGORITHM])
        subject = payload.get("sub")
        return int(subject) if subject is not None else None
    except (InvalidTokenError, TypeError, ValueError):
        return None