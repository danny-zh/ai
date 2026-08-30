from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from app.backend.models.habit import Habit, HabitCreateRequest, HabitUpdateRequest


class HabitStore:
    """Stores habit data in a JSON file on disk."""

    def __init__(self, file_path: str | Path | None = None) -> None:
        self.file_path = Path(file_path) if file_path is not None else Path("app/backend/data/habits.json")
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")

    def _read_all(self) -> List[Habit]:
        data = self.file_path.read_text(encoding="utf-8")
        if not data.strip():
            return []
        payload = json.loads(data)
        return [Habit.model_validate(item) for item in payload]

    def _write_all(self, habits: List[Habit]) -> None:
        payload = [habit.model_dump(mode="json") for habit in habits]
        self.file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def list_habits(self) -> List[Habit]:
        """Return all stored habits."""
        return self._read_all()

    def create_habit(self, payload: HabitCreateRequest) -> Habit:
        """Create a new habit from a request payload."""
        habits = self._read_all()
        habit = Habit(
            id=f"habit-{len(habits) + 1}-{payload.name.lower().replace(' ', '-')}",
            name=payload.name,
            color=payload.color,
            entries=payload.entries or {},
        )
        habits.append(habit)
        self._write_all(habits)
        return habit

    def get_habit(self, habit_id: str) -> Optional[Habit]:
        """Return a habit by identifier, if present."""
        for habit in self._read_all():
            if habit.id == habit_id:
                return habit
        return None

    def update_habit(self, habit_id: str, payload: HabitUpdateRequest) -> Habit:
        """Update a single habit by identifier."""
        habits = self._read_all()
        for index, habit in enumerate(habits):
            if habit.id == habit_id:
                updated = habit.model_copy(update={})
                if payload.name is not None:
                    updated.name = payload.name
                if payload.color is not None:
                    updated.color = payload.color
                if payload.entries is not None:
                    updated.entries = payload.entries
                habits[index] = updated
                self._write_all(habits)
                return updated
        raise KeyError(f"Habit with id '{habit_id}' not found")

    def delete_habit(self, habit_id: str) -> None:
        """Delete a habit by identifier."""
        habits = self._read_all()
        remaining = [habit for habit in habits if habit.id != habit_id]
        if len(remaining) == len(habits):
            raise KeyError(f"Habit with id '{habit_id}' not found")
        self._write_all(remaining)
