---
description: "Guidance for building and testing the Habit Tracker app: FastAPI backend + vanilla JS/HTML/CSS frontend, snake case naming, docstrings/JSDoc, testing conventions"
applyTo: "app/**"
---

# Habit Tracker — Agent Instructions

## Project Overview
Habit Tracker lets a user track one or many habits per day. Each habit has its own
table view for the current month in calendar view: rows represent the days of the month (1 → last
day), columns represent the habit and its per-day completion status.

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
| `test/` | Unit tests, mirroring the structure of `src/`, `models/`, `services/`, `utils/` |

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
Expose REST endpoints under FastAPI for:
- `GET/POST/habits` — list/create habits.
- `DELETE/PUT/PATCH /habits/{habitId}` — delete/update a specific habit.

data validation is performed both at the Pydantic model level and in the route handler. Return appropriate HTTP status codes and error messages for invalid requests. Use `HTTPException` for errors.

Responses are JSON and consumed by the frontend via `fetch` calls in
`frontend/services/`.

## Testing
- Backend: use `pytest` with `httpx.TestClient` (or Starlette's `TestClient`) against
  the FastAPI app. Place tests under `backend/test/`, one test module per source
  module in `src/`, `models/`, `services/`, `utils/`.
- Frontend: use `Jest`. Place tests under `frontend/test/`, one test module per
  source module in `src/`, `models/`, `services/`, `utils/`.
- Every new function/class in `services/`, `models/`, and `utils/` needs at least
  one corresponding unit test.
