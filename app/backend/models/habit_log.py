"""Pydantic schemas for daily habit-log APIs."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class HabitLogCreateRequest(BaseModel):
    """Request payload that creates or updates one daily log.

    Attributes:
        log_date: Date represented by the log.
        habit_duration: Completed duration in minutes.
    """

    log_date: date
    habit_duration: int = Field(default=60, ge=0)


class HabitLogUpdateRequest(BaseModel):
    """Request payload that changes a log duration.

    Attributes:
        habit_duration: Replacement completed duration in minutes.
    """

    habit_duration: int = Field(..., ge=0)


class HabitLog(BaseModel):
    """Public representation of a persisted daily habit log.

    Attributes:
        id_habit: Identifier of the logged habit.
        id_user: Identifier of the habit owner.
        habit_duration: Completed duration in minutes.
        log_date: Date represented by the log.
    """

    model_config = ConfigDict(from_attributes=True)

    id_habit: int
    id_user: int
    habit_duration: int
    log_date: date