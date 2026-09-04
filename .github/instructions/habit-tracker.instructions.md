---
description: "Guidance for building and testing the Habit Tracker app: FastAPI backend + vanilla JS/HTML/CSS frontend, snake case naming, docstrings/JSDoc, testing conventions"
applyTo: "app/**"
---

# Habit Tracker — Agent Instructions

## Project Overview
Habit Tracker lets a user track one or many habits per day. Habits are displayed in a month calendar view for the current month, with the ability to check previous or future months.

The user can create a new habit with a name, color, and description. The user can also edit or delete an existing habit. The user can add a log entry that can be checked or unchecked for each day of the displayed month view. Each log entry will have a duration in minutes (default 60 minutes) associated with it.
  
## Architecture
Two top-level apps under `app/`:

- `app/backend/` — FastAPI application.
- `app/frontend/` — vanilla JS/HTML/CSS application (no framework, no bundler unless
  already present).

Each app is organized the same way:

| Folder | Purpose |
|---|---|
| `src/` | Application entry points and route/UI handlers |
| `models/` | Data models (Pydantic models in backend, plain JS classes/objects in frontend) |
| `services/` | Business logic, orchestration, persistence access |
| `utils/` | Small stateless helpers |
| `routes/` | Route handlers (backend) or UI event handlers (frontend) |
| `test/` | Unit tests, mirroring the structure of `src/`, `models/`, `services/`, `utils/` |

## Data Model
Target entity-relationship shape (a `User` creates many `Habit`s and logs many
`HabitLog`s; a `Habit` has many `HabitLog`s):

- `User` — `id`, `username`, `email`, `password`.
- `Habit` — `id`, `name`, `color`, `description`, `pk_idUser` (owning user).
- `HabitLog` — `fk_idHabit`, `fk_idUser`, `habit_duration`, `log_date`.

## Naming Conventions
Use **snake case** for variable and function names in both Python and JavaScript

## Documentation
- Python: add a docstring to every function, class, and Pydantic model describing
  purpose, `Args`, and `Returns` (Google style), including parameter and return types.
- JavaScript: add a JSDoc block above every function and class using `@param`,
  `@returns`, and `@type` tags.
- Only document what the signature doesn't already make obvious — keep docstrings
  and JSDoc concise.

## Change Philosophy
- Prefer small, incremental changes over large refactors.
- Do not add external dependencies unless the task genuinely requires it. If one is to be added ask for discussion first.

## Data Persistence
Store habit and daily-entry data as JSON on disk (or in-memory for tests) via
`backend/services/`. Do not introduce a database or ORM dependency.

## API Contract (backend)
Target full CRUD contract for `User` ⇄ `Habit` ⇄ `HabitLog` (see `Data Model` above).
Route handlers live under `app/backend/routes/`; data validation is performed both at
the Pydantic model level and in the route handler. Return appropriate HTTP status
codes and error messages for invalid requests, and use `HTTPException` for errors.
Responses are JSON and consumed by the frontend via `fetch` calls in
`frontend/services/`.

### `User` CRUD
- `GET /users` — list users.
- `GET /users/{user_id}` — fetch a single user; `404` if not found.
- `POST /users` — create a user (`username`, `email`, `password`); reject duplicate
  `username`/`email` with `409 Conflict`.
- `PATCH /users/{user_id}` — partially update a user (optional `username`, `email`,
  `password`); `404` if not found, `409` on duplicate `username`/`email`.
- `DELETE /users/{user_id}` — delete a user (and, by cascade, their habits/logs);
  `404` if not found.

Never expose the raw `password` field in any response body.

### `Habit` CRUD
- `GET /users/{user_id}/habits` — list habits owned by a given user; `404` if the
  user does not exist.
- `POST /users/{user_id}/habits` — create a habit for that user
  (`HabitCreateRequest`: `name`, `color`, `description`); `404` if the user does not
  exist, `422` for invalid fields.
- `GET /habits/{habit_id}` — fetch a single habit; `404` if not found.
- `PATCH /habits/{habit_id}` — partially update a habit (`HabitUpdateRequest`:
  optional `name`, `color`, `description`); `404` if not found. There is no
  `PUT /habits/{habit_id}` endpoint — use `PATCH` for updates.
- `DELETE /habits/{habit_id}` — delete a habit (and, by cascade, its logs); `404` if
  not found.

### `HabitLog` CRUD
- `GET /habits/{habit_id}/logs` — list a habit's daily log entries; `404` if the
  habit does not exist.
- `POST /habits/{habit_id}/logs` — create/upsert a log entry for a `log_date`
  (`habit_duration` in minutes, default `60`; `log_date`); `user_id` is inferred
  from the owning habit; `404` if the habit does not exist, `422` for invalid fields.
- `PATCH /habits/{habit_id}/logs/{log_date}` — update `habit_duration` for an
  existing log entry; `404` if the habit or log entry does not exist.
- `DELETE /habits/{habit_id}/logs/{log_date}` — remove a single day's log entry;
  `404` if not found.

## Testing
- Backend: use `pytest` with `httpx.TestClient` (or Starlette's `TestClient`) against
  the FastAPI app. Place tests under `backend/test/`, one test module per source
  module in `src/`, `models/`, `services/`, `utils/`.
- Frontend: use `Jest`. Place tests under `frontend/test/`, one test module per
  source module in `src/`, `models/`, `services/`, `utils/`.
- Every new function/class in `services/`, `models/`, and `utils/` needs at least
  one corresponding unit test.
