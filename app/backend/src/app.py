from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.backend.models.habit import Habit, HabitCreateRequest, HabitUpdateRequest
from app.backend.services.habit_store import HabitStore

app = FastAPI(title="Habit Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = HabitStore()


@app.get("/habits", response_model=list[Habit])
def list_habits() -> list[Habit]:
    """Return every saved habit."""
    return store.list_habits()


@app.post("/habits", response_model=Habit, status_code=201)
def create_habit(payload: HabitCreateRequest) -> Habit:
    """Create a new habit."""
    try:
        return store.create_habit(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.patch("/habits/{habit_id}", response_model=Habit)
def update_habit(habit_id: str, payload: HabitUpdateRequest) -> Habit:
    """Update an existing habit."""
    try:
        return store.update_habit(habit_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/habits/{habit_id}", status_code=204)
def delete_habit(habit_id: str) -> None:
    """Delete a habit by identifier."""
    try:
        store.delete_habit(habit_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
