# Habit Tracker Database Layer

This directory builds the MySQL 8.4 image used by the Habit Tracker backend. The
image initializes the `habitdb` schema from version-controlled SQL and provides a
health check for local Compose and integration-test startup.

## Contents

| Path | Purpose |
| --- | --- |
| `Dockerfile` | MySQL 8.4 image, initialization-script copy, port declaration, and health check |
| `scripts/sql/01_init.sql` | Creates `habitdb` and its relational tables and constraints |
| `scripts/sql/02_data_population.sql` | Creates reproducible development seed data |
| `test/test_database.py` | Builds and validates a disposable instance of this image |
| `makefile` | Local image build, run, remove, and test targets |

## Schema

The image creates the following InnoDB tables with `utf8mb4`:

- `user`: user ID, unique username, unique email, and password hash.
- `habit`: a user-owned habit with name, color, and optional description.
- `habit_log`: one daily duration record per habit and date.

The schema enforces unique usernames and emails, non-negative log durations,
habit ownership for log entries, and cascading deletes from users to habits and
logs. The FastAPI backend maps this existing schema through SQLAlchemy; this
image remains the source of schema initialization.

## Build and Run

Run these commands from this directory:

```bash
make build-database
MYSQL_ROOT_PASSWORD='choose-a-local-database-password' make run-database
```

The default image is `habitdb-implementation-check:1.0.0`, the default container
name is `habitdb`, and MySQL is published at `localhost:3306`. Override any of
them when needed:

```bash
make build-database DATABASE_IMAGE=habitdb:local
MYSQL_ROOT_PASSWORD='choose-a-local-database-password' \
  make run-database DATABASE_IMAGE=habitdb:local DATABASE_CONTAINER_NAME=habitdb-local PORT_MAPPING=3307:3306
```

The `run-database` target removes a same-named existing container first. Stop and
remove the local container with:

```bash
make remove-database DATABASE_CONTAINER_NAME=habitdb-local
```

The repository-root Compose workflow is the preferred way to run the database
with the FastAPI backend. See [../../README.md](../../README.md) for that flow.

## Inspecting Data

After the container is healthy, list the initialized tables with:

```bash
docker exec --env MYSQL_PWD='choose-a-local-database-password' habitdb \
  mysql --user=root --execute 'SHOW TABLES FROM habitdb;'
```

The backend connects with a SQLAlchemy URL in this form:

```text
mysql+pymysql://root:<password>@<host>:3306/habitdb
```

Use the Compose hostname `database` when the backend runs in the Compose network.

## Initialization and Seed Data

MySQL's official entrypoint runs files in `/docker-entrypoint-initdb.d/` in
lexical order when `/var/lib/mysql` is empty:

1. `01_init.sql` creates the database, tables, foreign keys, unique constraints,
   and duration check.
2. `02_data_population.sql` creates `demo_user`, five habits, and deterministic
   August 2026 habit logs.

The population script is idempotent when sourced again: it does not duplicate the
demo user, habits, or log dates. The seeded password is a non-bcrypt placeholder
and cannot authenticate through the FastAPI API. Register an account through the
backend instead.

Changing either SQL script does not alter an already initialized data directory.
For disposable local data, remove the attached MySQL volume and start a fresh
container. For persistent environments, apply an explicit migration rather than
relying on entrypoint initialization.

## Tests

Run the database integration suite from this directory:

```bash
make test-database
```

Or run it from the repository root:

```bash
make test-database
```

The suite requires Docker and pytest. It builds a disposable image, waits for the
health check, and verifies schema metadata, constraints, foreign keys, cascades,
seed-data initialization, and idempotent reseeding. It removes the temporary
container and image during teardown.

The local target defaults to `../../.venv/bin/python`; override it with, for
example, `make test-database PYTHON=python3` when pytest is installed elsewhere.
