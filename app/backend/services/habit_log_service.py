"""Database-backed operations for daily habit logs."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.backend.models.habit_log import HabitLogCreateRequest, HabitLogUpdateRequest
from app.backend.models.orm import HabitLogRecord
from app.backend.services.errors import ResourceNotFoundError


class HabitLogService:
    """Manage logs only through their authenticated habit owner."""

    def __init__(self, session: Session) -> None:
        """Initialize the service.

        Args:
            session: Open database session used by service methods.
        """
        self.session = session

    def list_for_habit(self, habit_id: int, user_id: int) -> list[HabitLogRecord]:
        """List a user's logs for one habit.

        Args:
            habit_id: Habit identifier.
            user_id: Owning user identifier.

        Returns:
            Ordered list of daily logs.
        """
        statement = select(HabitLogRecord).where(
            HabitLogRecord.id_habit == habit_id,
            HabitLogRecord.id_user == user_id,
        ).order_by(HabitLogRecord.log_date)
        return list(self.session.scalars(statement))

    def get(self, habit_id: int, user_id: int, log_date: date) -> HabitLogRecord:
        """Return a daily log scoped to its owner.

        Args:
            habit_id: Habit identifier.
            user_id: Owning user identifier.
            log_date: Logged date.

        Returns:
            Persisted daily log.

        Raises:
            ResourceNotFoundError: If no matching owned log exists.
        """
        statement = select(HabitLogRecord).where(
            HabitLogRecord.id_habit == habit_id,
            HabitLogRecord.id_user == user_id,
            HabitLogRecord.log_date == log_date,
        )
        habit_log = self.session.scalar(statement)
        if habit_log is None:
            raise ResourceNotFoundError("Habit log not found")
        return habit_log

    def upsert(
        self,
        habit_id: int,
        user_id: int,
        payload: HabitLogCreateRequest,
    ) -> tuple[HabitLogRecord, bool]:
        """Create or update one daily habit log.

        Args:
            habit_id: Habit identifier.
            user_id: Verified owner identifier inferred from the habit.
            payload: Validated daily log request.

        Returns:
            The persisted log and whether it was newly created.
        """
        try:
            habit_log = self.get(habit_id, user_id, payload.log_date)
            habit_log.habit_duration = payload.habit_duration
            created = False
        except ResourceNotFoundError:
            habit_log = HabitLogRecord(
                id_habit=habit_id,
                id_user=user_id,
                log_date=payload.log_date,
                habit_duration=payload.habit_duration,
            )
            self.session.add(habit_log)
            created = True
        self.session.commit()
        self.session.refresh(habit_log)
        return habit_log, created

    def update(
        self,
        habit_id: int,
        user_id: int,
        log_date: date,
        payload: HabitLogUpdateRequest,
    ) -> HabitLogRecord:
        """Update the duration on an existing daily habit log.

        Args:
            habit_id: Habit identifier.
            user_id: Owning user identifier.
            log_date: Logged date.
            payload: Validated duration update.

        Returns:
            Updated daily log.

        Raises:
            ResourceNotFoundError: If no matching owned log exists.
        """
        habit_log = self.get(habit_id, user_id, log_date)
        habit_log.habit_duration = payload.habit_duration
        self.session.commit()
        self.session.refresh(habit_log)
        return habit_log

    def delete(self, habit_id: int, user_id: int, log_date: date) -> None:
        """Delete one owned daily habit log.

        Args:
            habit_id: Habit identifier.
            user_id: Owning user identifier.
            log_date: Logged date.

        Raises:
            ResourceNotFoundError: If no matching owned log exists.
        """
        self.session.delete(self.get(habit_id, user_id, log_date))
        self.session.commit()