"""Protected routes for daily logs on owned habits."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.backend.database import get_session
from app.backend.models.habit_log import HabitLog, HabitLogCreateRequest, HabitLogUpdateRequest
from app.backend.security.auth import get_current_user
from app.backend.services.errors import ResourceNotFoundError
from app.backend.services.habit_log_service import HabitLogService
from app.backend.services.habit_service import HabitService


router = APIRouter(prefix="/habits/{habit_id}/logs", tags=["habit logs"])


def get_owned_habit(habit_id: int, user_id: int, session: Session) -> None:
    """Ensure a habit exists and belongs to the authenticated user.

    Args:
        habit_id: Habit identifier from the path.
        user_id: Authenticated user identifier.
        session: Database session for the request.

    Raises:
        HTTPException: If the habit is missing or belongs to another user.
    """
    try:
        HabitService(session).get_for_user(habit_id, user_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("", response_model=list[HabitLog])
def list_habit_logs(
    habit_id: int,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[HabitLog]:
    """List logs for an owned habit."""
    get_owned_habit(habit_id, current_user_id, session)
    return [HabitLog.model_validate(habit_log) for habit_log in HabitLogService(session).list_for_habit(habit_id, current_user_id)]


@router.post("", response_model=HabitLog)
def upsert_habit_log(
    habit_id: int,
    payload: HabitLogCreateRequest,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response | HabitLog:
    """Create or update a daily log for an owned habit."""
    get_owned_habit(habit_id, current_user_id, session)
    habit_log, created = HabitLogService(session).upsert(habit_id, current_user_id, payload)
    response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return Response(
        content=HabitLog.model_validate(habit_log).model_dump_json(),
        media_type="application/json",
        status_code=response_status,
    )


@router.patch("/{log_date}", response_model=HabitLog)
def update_habit_log(
    habit_id: int,
    log_date: date,
    payload: HabitLogUpdateRequest,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> HabitLog:
    """Update the duration for an existing owned habit log."""
    get_owned_habit(habit_id, current_user_id, session)
    try:
        return HabitLog.model_validate(HabitLogService(session).update(habit_id, current_user_id, log_date, payload))
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{log_date}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit_log(
    habit_id: int,
    log_date: date,
    current_user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response:
    """Delete one daily log for an owned habit."""
    get_owned_habit(habit_id, current_user_id, session)
    try:
        HabitLogService(session).delete(habit_id, current_user_id, log_date)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)