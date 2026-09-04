"""Protected self-service user profile routes."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.backend.database import get_session
from app.backend.models.user import User, UserUpdateRequest
from app.backend.security.auth import get_current_user
from app.backend.services.errors import DuplicateUserError, ResourceNotFoundError
from app.backend.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])


def require_self(user_id: int, current_user_id: int) -> None:
    """Require a path user identifier to match the authenticated user.

    Args:
        user_id: User identifier supplied in the request path.
        current_user_id: Identifier authenticated from the bearer token.

    Raises:
        HTTPException: If the requested user differs from the authenticated user.
    """
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    """Return the authenticated user's profile."""
    require_self(user_id, current_user_id)
    try:
        return User.model_validate(UserService(session).get(user_id))
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> User:
    """Update the authenticated user's profile."""
    require_self(user_id, current_user_id)
    try:
        return User.model_validate(UserService(session).update(user_id, payload))
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DuplicateUserError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response:
    """Delete the authenticated user's account and owned resources."""
    require_self(user_id, current_user_id)
    try:
        UserService(session).delete(user_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)