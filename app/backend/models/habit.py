from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Habit(BaseModel):
    """Represents a persisted habit.

    Attributes:
        id: Unique habit identifier.
        name: Habit name.
        color: Habit color used in the UI.
        description: Optional habit description.
        id_user: Identifier of the owning user.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique habit identifier.")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the habit.")
    color: str = Field(..., max_length=32, description="Habit color used in the UI.")
    description: Optional[str] = Field(default=None, description="Optional habit description.")
    id_user: int = Field(..., description="Identifier of the owning user.")


class HabitCreateRequest(BaseModel):
    """Request payload used when creating a habit.

    Attributes:
        name: Habit name.
        color: Habit color used in the UI.
        description: Optional habit description.
    """

    name: str = Field(..., min_length=1, max_length=100, description="Habit name.")
    color: str = Field(..., min_length=1, max_length=32, description="Habit color used in the UI.")
    description: Optional[str] = Field(default=None, description="Optional habit description.")


class HabitUpdateRequest(BaseModel):
    """Request payload used when updating a habit.

    Attributes:
        name: Updated habit name.
        color: Updated habit color.
        description: Updated optional habit description.
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Updated name.")
    color: Optional[str] = Field(default=None, min_length=1, max_length=32, description="Updated color.")
    description: Optional[str] = Field(default=None, description="Updated optional description.")
