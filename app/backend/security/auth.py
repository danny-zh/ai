"""FastAPI dependency for bearer-token authentication."""

from typing import Annotated

from fastapi import Header, HTTPException, status

from app.backend.security.tokens import verify_access_token


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> int:
    """Extract the authenticated user ID from a bearer token.

    Args:
        authorization: HTTP Authorization header.

    Returns:
        Authenticated user identifier.

    Raises:
        HTTPException: If the bearer token is missing or invalid.
    """
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    user_id = verify_access_token(authorization.removeprefix("Bearer "))
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return user_id