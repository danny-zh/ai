# ai
A simple repo for playing with AI stuff

## Habit Tracker

The Habit Tracker API uses FastAPI, SQLAlchemy, and MySQL 8.4. The database
stores users, their habits, and per-day habit durations. All personal-resource
endpoints require an eight-hour bearer JWT issued after registration and login.

Set local-only secrets before starting the Compose stack:

```bash
export MYSQL_ROOT_PASSWORD='choose-a-local-database-password'
export JWT_SECRET_KEY='generate-a-long-random-secret-for-local-use'
make up-habit-tracker
```

The API is available at `http://localhost:8001`. Stop the stack with
`make down-habit-tracker`, or follow its logs with `make logs-habit-tracker`.
The MySQL service is private to the Compose network. FastAPI's interactive API
documentation is available at `http://localhost:8001/docs`.

Register a user, log in, and pass the returned token as an Authorization header:

```bash
curl --request POST http://localhost:8001/auth/register \
  --header 'Content-Type: application/json' \
  --data '{"username":"alex","email":"alex@example.com","password":"correct-horse-battery-staple"}'

curl --request POST http://localhost:8001/auth/login \
  --header 'Content-Type: application/json' \
  --data '{"username":"alex","password":"correct-horse-battery-staple"}'
```

Use `Authorization: Bearer <access_token>` for `GET`, `PATCH`, and `DELETE`
`/users/{user_id}`; `GET` and `POST` `/users/{user_id}/habits`; and all
`/habits/{habit_id}/logs` endpoints. The token holder can access only their own
profile, habits, and logs. There is no global user or habit listing endpoint.

For the complete authenticated API request/response contract, configuration
reference, and database reset procedure, see [app/backend/README.md](app/backend/README.md).

The database image initializes `habitdb` and its `user`, `habit`, and
`habit_log` tables. Its scripts run only against an empty MySQL volume. It also
creates a `demo_user` with sample habits and August 2026 log data; the seed
password is a non-login placeholder, so register an API account for use with
the backend.

Run the database image and backend API integration suites with Docker and
pytest available:

```bash
make test-database
make test-backend
```

Both Make targets use `.venv/bin/python` by default. Override it when needed,
for example with `make test-backend PYTHON=python3`.

The MySQL initialization scripts run only for an empty `habitdb_data` volume. To
reset local sample data, run `docker compose down --volumes` and then start the
stack again with `make up-habit-tracker` and the required environment variables.

The existing browser frontend is not yet compatible with this authenticated API:
it does not register/log in, send bearer tokens, or load separate log records.
