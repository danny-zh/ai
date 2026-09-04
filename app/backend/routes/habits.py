"""Protected routes for habits owned by the authenticated user."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.backend.database import get_session
from app.backend.models.habit import Habit, HabitCreateRequest, HabitUpdateRequest
from app.backend.security.auth import get_current_user
from app.backend.services.errors import ResourceNotFoundError
from app.backend.services.habit_service import HabitService
from app.backend.services.user_service import UserService


router = APIRouter(tags=["habits"])


def require_owner_path(user_id: int, current_user_id: int) -> None:
    """Require a nested user path to match the authenticated user.

    Args:
        user_id: User identifier supplied in the request path.
        current_user_id: Identifier authenticated from the bearer token.

    Raises:
        HTTPException: If the requested user differs from the authenticated user.
    """
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("/users/{user_id}/habits", response_model=list[Habit])
def list_habits(
    user_id: int,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Habit]:
    """List habits owned by the authenticated user."""
    require_owner_path(user_id, current_user_id)
    try:
        UserService(session).get(user_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [Habit.model_validate(habit) for habit in HabitService(session).list_for_user(user_id)]


@router.post("/users/{user_id}/habits", response_model=Habit, status_code=status.HTTP_201_CREATED)
def create_habit(
    user_id: int,
    payload: HabitCreateRequest,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Habit:
    """Create a habit for the authenticated user."""
    require_owner_path(user_id, current_user_id)
    try:
        UserService(session).get(user_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Habit.model_validate(HabitService(session).create(user_id, payload))


@router.get("/habits/{habit_id}", response_model=Habit)
def get_habit(
    habit_id: int,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Habit:
    """Return an owned habit by identifier."""
    try:
        return Habit.model_validate(HabitService(session).get_for_user(habit_id, current_user_id))
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/habits/{habit_id}", response_model=Habit)
def update_habit(
    habit_id: int,
    payload: HabitUpdateRequest,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Habit:
    """Update an owned habit by identifier."""
    try:
        return Habit.model_validate(HabitService(session).update(habit_id, current_user_id, payload))
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: int,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response:
    """Delete an owned habit by identifier."""
    try:
        HabitService(session).delete(habit_id, current_user_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)