# Habit Tracker Backend API

The backend is a synchronous FastAPI application backed by MySQL through
SQLAlchemy. It has no file-based persistence. The database schema is initialized
by `app/database/scripts/sql/01_init.sql`; the application expects that schema to
exist and does not create or migrate tables itself.

## Configuration

The backend requires these environment variables:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy MySQL URL, such as `mysql+pymysql://root:password@database:3306/habitdb` |
| `JWT_SECRET_KEY` | Secret used to sign and verify access tokens; provide a long random value |

Access tokens use HS256 and expire eight hours after login. The Compose service
sets `DATABASE_URL` automatically and requires `MYSQL_ROOT_PASSWORD` and
`JWT_SECRET_KEY` from the shell environment.

## Authentication

Only account registration and login are public. All other requests must include:

```http
Authorization: Bearer <access_token>
```

| Method | Path | Body | Success |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | `username`, `email`, `password` | `201` with `id`, `username`, `email` |
| `POST` | `/auth/login` | `username`, `password` | `200` with `access_token`, `token_type`, `user_id`, `username` |

Usernames are at most 100 characters, emails at most 254 characters, and
registration passwords must be 8 to 128 characters. Passwords are stored as
bcrypt hashes and are never returned in API responses. Duplicate usernames or
emails return `409`; invalid login credentials return `401`.

## Protected Resources

An access token is limited to its own user profile and resource tree. There is no
global user list, global habit list, or role-based administration endpoint.

| Method | Path | Body | Success |
| --- | --- | --- | --- |
| `GET` | `/users/{user_id}` | None | `200` user profile |
| `PATCH` | `/users/{user_id}` | Any of `username`, `email`, `password` | `200` user profile |
| `DELETE` | `/users/{user_id}` | None | `204` |
| `GET` | `/users/{user_id}/habits` | None | `200` habit list |
| `POST` | `/users/{user_id}/habits` | `name`, `color`, optional `description` | `201` habit |
| `GET` | `/habits/{habit_id}` | None | `200` habit |
| `PATCH` | `/habits/{habit_id}` | Any of `name`, `color`, `description` | `200` habit |
| `DELETE` | `/habits/{habit_id}` | None | `204` |
| `GET` | `/habits/{habit_id}/logs` | None | `200` log list |
| `POST` | `/habits/{habit_id}/logs` | `log_date`, optional `habit_duration` | `201` or `200` |
| `PATCH` | `/habits/{habit_id}/logs/{log_date}` | `habit_duration` | `200` log |
| `DELETE` | `/habits/{habit_id}/logs/{log_date}` | None | `204` |

A habit response contains `id`, `name`, `color`, `description`, and `id_user`.
A log response contains `id_habit`, `id_user`, `habit_duration`, and `log_date`.
`log_date` is an ISO date (`YYYY-MM-DD`) and `habit_duration` is a non-negative
integer in minutes that defaults to `60` on creation.

Posting a log for a habit/date creates it on the first request (`201`) or updates
its duration on later requests (`200`). The server derives the log owner from the
habit; clients cannot supply an `id_user`.

Missing or invalid bearer tokens return `401`. Supplying a different user ID in a
nested `/users/{user_id}` path returns `403`. Habits and logs that are missing or
belong to a different user return `404`.

## Local Development

From the repository root, start the complete stack:

```bash
export MYSQL_ROOT_PASSWORD='choose-a-local-database-password'
export JWT_SECRET_KEY='generate-a-long-random-secret-for-local-use'
make up-habit-tracker
```

The API runs on `http://localhost:8001`; FastAPI's interactive schema is at
`http://localhost:8001/docs`. The MySQL server is intentionally available only
inside the Compose network.

```bash
make logs-habit-tracker
make down-habit-tracker
```

MySQL initialization scripts run only when the named `habitdb_data` volume is
empty. To recreate it and rerun the schema and sample-data scripts, stop the
stack with `docker compose down --volumes`, then start it again with the required
environment variables.

## Tests

Both test suites require Docker and pytest. They build disposable MySQL images
and remove their containers and images after each module:

```bash
make test-database
make test-backend
```

Set `PYTHON=python3` when pytest is installed outside the repository `.venv`.