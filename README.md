# ai
A simple repo for playing with AI stuff

## Habit Tracker database

The database image initializes a MySQL 8.4 instance with the `habitdb` database
and the `user`, `habit`, and `habit_log` tables. MySQL listens on its default
container port, `3306`. It also creates a `demo_user` account with the Study,
Read, Workout, Travel, and Dance habits and reproducible sample completion data
for August 2026.

Build and run the image with a fresh data volume:

```bash
docker build -t habitdb:local app/database
docker run --detach \
	--name habitdb \
	--env MYSQL_ROOT_PASSWORD=local-root-password \
	--publish 3306:3306 \
	--volume habitdb-data:/var/lib/mysql \
	habitdb:local
```

After the container is healthy, inspect the initialized tables:

```bash
docker exec --env MYSQL_PWD=local-root-password habitdb \
	mysql --user=root --execute "SHOW TABLES FROM habitdb;"
```

The schema and population scripts run only when MySQL starts with an empty data
directory. The population script is safe to run again manually and does not
duplicate its demo records. Use migrations for later schema changes, or recreate
the named volume when working with disposable local data.

Run the Docker integration tests with Docker and pytest available:

```bash
make test-database
```

The Make target uses `.venv/bin/python` by default. Override it when needed, for
example with `make test-database PYTHON=python3`.
