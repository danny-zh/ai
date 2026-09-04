"""Database-backed operations for habits owned by one user."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.backend.models.habit import HabitCreateRequest, HabitUpdateRequest
from app.backend.models.orm import HabitRecord
from app.backend.services.errors import ResourceNotFoundError


class HabitService:
    """Manage habits with ownership enforced by query scope."""

    def __init__(self, session: Session) -> None:
        """Initialize the service.

        Args:
            session: Open database session used by service methods.
        """
        self.session = session

    def list_for_user(self, user_id: int) -> list[HabitRecord]:
        """List habits owned by a user.

        Args:
            user_id: Owning user identifier.

        Returns:
            Ordered list of the user's habits.
        """
        statement = select(HabitRecord).where(HabitRecord.id_user == user_id).order_by(HabitRecord.id)
        return list(self.session.scalars(statement))

    def create(self, user_id: int, payload: HabitCreateRequest) -> HabitRecord:
        """Create a habit for a user.

        Args:
            user_id: Owning user identifier.
            payload: Validated habit creation request.

        Returns:
            Newly persisted habit record.
        """
        habit = HabitRecord(id_user=user_id, **payload.model_dump())
        self.session.add(habit)
        self.session.commit()
        self.session.refresh(habit)
        return habit

    def get_for_user(self, habit_id: int, user_id: int) -> HabitRecord:
        """Return a habit only when it belongs to the specified user.

        Args:
            habit_id: Habit identifier.
            user_id: Owning user identifier.

        Returns:
            Persisted habit record.

        Raises:
            ResourceNotFoundError: If no owned habit matches.
        """
        statement = select(HabitRecord).where(HabitRecord.id == habit_id, HabitRecord.id_user == user_id)
        habit = self.session.scalar(statement)
        if habit is None:
            raise ResourceNotFoundError("Habit not found")
        return habit

    def update(self, habit_id: int, user_id: int, payload: HabitUpdateRequest) -> HabitRecord:
        """Update a habit owned by a user.

        Args:
            habit_id: Habit identifier.
            user_id: Owning user identifier.
            payload: Validated partial habit update.

        Returns:
            Updated habit record.

        Raises:
            ResourceNotFoundError: If no owned habit matches.
        """
        habit = self.get_for_user(habit_id, user_id)
        for field_name, value in payload.model_dump(exclude_unset=True).items():
            setattr(habit, field_name, value)
        self.session.commit()
        self.session.refresh(habit)
        return habit

    def delete(self, habit_id: int, user_id: int) -> None:
        """Delete a habit owned by a user.

        Args:
            habit_id: Habit identifier.
            user_id: Owning user identifier.

        Raises:
            ResourceNotFoundError: If no owned habit matches.
        """
        self.session.delete(self.get_for_user(habit_id, user_id))
        self.session.commit()