from app.backend.models.habit import HabitCreateRequest, HabitUpdateRequest
from app.backend.services.habit_store import HabitStore


def test_create_habit_persists_a_new_record(tmp_path):
    store = HabitStore(file_path=tmp_path / "habits.json")

    habit = store.create_habit(HabitCreateRequest(name="Read", color="#22c55e", entries={"2026-08-29": True}))

    assert habit.name == "Read"
    assert habit.color == "#22c55e"
    assert store.list_habits()[0].id == habit.id


def test_update_habit_changes_existing_values(tmp_path):
    store = HabitStore(file_path=tmp_path / "habits.json")
    habit = store.create_habit(HabitCreateRequest(name="Workout", color="#4f46e5", entries={}))

    updated = store.update_habit(habit.id, HabitUpdateRequest(entries={"2026-08-30": True}, color="#10b981"))

    assert updated.entries["2026-08-30"] is True
    assert updated.color == "#10b981"


def test_delete_habit_removes_existing_record(tmp_path):
    store = HabitStore(file_path=tmp_path / "habits.json")
    habit = store.create_habit(HabitCreateRequest(name="Meditate", color="#a855f7", entries={}))

    store.delete_habit(habit.id)

    assert store.list_habits() == []
