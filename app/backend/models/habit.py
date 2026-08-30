from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel, Field


class Habit(BaseModel):
    """Represents a single habit and its daily completion record."""

    id: str = Field(..., description="Unique habit identifier.")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the habit.")
    color: str = Field(default="#4f46e5", description="Habit color used in the UI.")
    entries: Dict[str, bool] = Field(default_factory=dict, description="Map of date string to completion state.")


class HabitCreateRequest(BaseModel):
    """Request payload used when creating a new habit."""

    name: str = Field(..., min_length=1, max_length=100, description="Habit name.")
    color: str = Field(default="#4f46e5", description="Habit color used in the UI.")
    entries: Optional[Dict[str, bool]] = Field(default_factory=dict, description="Daily completion entries.")


class HabitUpdateRequest(BaseModel):
    """Request payload used when updating a habit."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Updated name.")
    color: Optional[str] = Field(default=None, description="Updated color.")
    entries: Optional[Dict[str, bool]] = Field(default=None, description="Updated completion record.")
