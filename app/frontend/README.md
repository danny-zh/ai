# Habit Tracker Frontend

Vanilla JavaScript frontend for the Habit Tracker app. It is served as static
files and talks to the FastAPI backend over HTTP.

## Run With Docker Compose

From the repository root, set the backend secrets and start the full stack:

```bash
export MYSQL_ROOT_PASSWORD='choose-a-local-database-password'
export JWT_SECRET_KEY='generate-a-long-random-secret-for-local-use'
make up-app
```

Open the frontend at `http://localhost:8000`. The backend API is available at
`http://localhost:8001`.

The frontend service is defined in `compose.yaml` and built from
`app/frontend/Dockerfile`, which serves this directory with nginx.

## Local Development

Because the frontend is static, it can also be opened directly from
`index.html` after the backend is running. Docker Compose is preferred for a
full-app check because it serves the page from `http://localhost:8000` while the
API remains on `http://localhost:8001`.

## Backend Integration

The frontend uses the backend as the source of truth. It does not reshape API
responses into the removed legacy `Habit` model.

Authentication flow:

- `POST /auth/register` creates a user.
- `POST /auth/login` returns a bearer token, user id, and username.
- The token session is stored locally by `services/auth_session.js`.
- Protected habit and log requests send `Authorization: Bearer <token>`.
- Logout clears the saved session and hides the authenticated app UI.

Habit data flow:

- Habits are backend-shaped records: `{ id, name, color, description, id_user }`.
- Habit logs are backend-shaped records: `{ id_habit, id_user, habit_duration, log_date }`.
- The calendar derives completion state from habit logs keyed by habit id.
- Toggling a day on creates or updates a log with the default duration of 60 minutes.
- Toggling a day off deletes that date's log.

## Project Structure

```text
index.html              Static app shell and auth forms
styles.css              App, auth, calendar, and responsive styles
Dockerfile              nginx static frontend image
services/auth_api.js    Registration and login API calls
services/auth_session.js Local session persistence
services/habit_api.js   Authenticated habit and habit-log API calls
src/app.js              App state helpers and habit-list rendering
src/calendar_view.js    Calendar rendering from backend-shaped logs
src/main.js             Browser event handlers and app lifecycle
utils/date_utils.js     Date formatting and month grid helpers
test/                   Jest tests
```

## Tests

Install dependencies once, then run Jest from this directory:

```bash
npm install
npm test
```

The tests cover auth API calls, local session persistence, backend-shaped habit
and log API requests, app state helpers, and date utilities.