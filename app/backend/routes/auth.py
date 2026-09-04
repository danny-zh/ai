"""Public account registration and login routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.backend.database import get_session
from app.backend.models.user import LoginRequest, TokenResponse, User, UserRegistrationRequest
from app.backend.security.tokens import create_access_token
from app.backend.services.errors import DuplicateUserError
from app.backend.services.user_service import UserService


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegistrationRequest, session: Session = Depends(get_session)) -> User:
    """Register a user account.

    Args:
        payload: Validated account registration data.
        session: Database session for the request.

    Returns:
        Newly registered user without a password.

    Raises:
        HTTPException: If username or email is already registered.
    """
    try:
        return User.model_validate(UserService(session).register(payload))
    except DuplicateUserError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    """Authenticate a user and return an access token.

    Args:
        payload: Validated login credentials.
        session: Database session for the request.

    Returns:
        Signed bearer-token response.

    Raises:
        HTTPException: If credentials are invalid.
    """
    user = UserService(session).authenticate(payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(
        access_token=create_access_token(user.id, user.username),
        user_id=user.id,
        username=user.username,
    )