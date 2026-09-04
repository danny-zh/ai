"""Integration tests for the Habit Tracker MySQL image."""

from __future__ import annotations

import subprocess
import time
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest


DATABASE_DIRECTORY = Path(__file__).resolve().parents[1]
TEST_ROOT_PASSWORD = "test-root-password"


def run_command(*command: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command and capture its text output.

    Args:
        *command: Executable and arguments to run.
        check: Whether a non-zero exit status should raise an exception.

    Returns:
        The completed process and its captured output.
    """
    return subprocess.run(command, check=check, capture_output=True, text=True)


def run_mysql(container_name: str, sql: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Execute SQL in a running test container.

    Args:
        container_name: Docker container that hosts MySQL.
        sql: SQL statement or statements to execute.
        check: Whether a MySQL error should raise an exception.

    Returns:
        The completed MySQL client process.
    """
    return run_command(
        "docker",
        "exec",
        "--env",
        f"MYSQL_PWD={TEST_ROOT_PASSWORD}",
        container_name,
        "mysql",
        "--user=root",
        "--batch",
        "--skip-column-names",
        "--execute",
        sql,
        check=check,
    )


@pytest.fixture(scope="module")
def mysql_container() -> Iterator[str]:
    """Build and start a disposable Habit Tracker MySQL container.

    Yields:
        The name of a healthy MySQL container.
    """
    docker_status = run_command("docker", "info", check=False)
    if docker_status.returncode != 0:
        pytest.skip(f"Docker is unavailable: {docker_status.stderr.strip()}")

    suffix = uuid.uuid4().hex[:12]
    image_name = f"habitdb-test:{suffix}"
    container_name = f"habitdb-test-{suffix}"

    try:
        run_command("docker", "build", "--tag", image_name, str(DATABASE_DIRECTORY))
        run_command(
            "docker",
            "run",
            "--detach",
            "--name",
            container_name,
            "--env",
            f"MYSQL_ROOT_PASSWORD={TEST_ROOT_PASSWORD}",
            image_name,
        )

        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            health = run_command(
                "docker",
                "inspect",
                "--format={{if .State.Health}}{{.State.Health.Status}}{{end}}",
                container_name,
                check=False,
            )
            if health.stdout.strip() == "healthy":
                break
            if health.returncode != 0 or health.stdout.strip() == "unhealthy":
                logs = run_command("docker", "logs", container_name, check=False)
                pytest.fail(f"MySQL failed to start:\n{logs.stdout}\n{logs.stderr}")
            time.sleep(1)
        else:
            logs = run_command("docker", "logs", container_name, check=False)
            pytest.fail(f"MySQL did not become healthy:\n{logs.stdout}\n{logs.stderr}")

        yield container_name
    finally:
        run_command("docker", "rm", "--force", container_name, check=False)
        run_command("docker", "image", "rm", "--force", image_name, check=False)


def test_database_schema(mysql_container: str) -> None:
    """Validate the initialized database tables, columns, and constraints."""
    schema = run_mysql(
        mysql_container,
        """
        SELECT SCHEMA_NAME
        FROM information_schema.SCHEMATA
        WHERE SCHEMA_NAME = 'habitdb';

        SELECT TABLE_NAME
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = 'habitdb'
        ORDER BY TABLE_NAME;

        SELECT CONCAT_WS('|', TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE,
                         COALESCE(COLUMN_DEFAULT, 'NULL'), EXTRA)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = 'habitdb'
        ORDER BY TABLE_NAME, ORDINAL_POSITION;
        """,
    ).stdout.splitlines()

    assert schema == [
        "habitdb",
        "habit",
        "habit_log",
        "user",
        "habit|id|bigint unsigned|NO|NULL|auto_increment",
        "habit|name|varchar(100)|NO|NULL|",
        "habit|color|varchar(32)|NO|NULL|",
        "habit|description|text|YES|NULL|",
        "habit|id_user|bigint unsigned|NO|NULL|",
        "habit_log|id_habit|bigint unsigned|NO|NULL|",
        "habit_log|id_user|bigint unsigned|NO|NULL|",
        "habit_log|habit_duration|int unsigned|NO|60|",
        "habit_log|log_date|date|NO|NULL|",
        "user|id|bigint unsigned|NO|NULL|auto_increment",
        "user|username|varchar(100)|NO|NULL|",
        "user|email|varchar(254)|NO|NULL|",
        "user|password|varchar(255)|NO|NULL|",
    ]

    constraints = run_mysql(
        mysql_container,
        """
        SELECT CONCAT_WS('|', TABLE_NAME, CONSTRAINT_NAME, CONSTRAINT_TYPE)
        FROM information_schema.TABLE_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = 'habitdb'
        ORDER BY TABLE_NAME, CONSTRAINT_NAME;

        SELECT CONCAT_WS('|', TABLE_NAME, CONSTRAINT_NAME,
                         REFERENCED_TABLE_NAME, UPDATE_RULE, DELETE_RULE)
        FROM information_schema.REFERENTIAL_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = 'habitdb'
        ORDER BY TABLE_NAME, CONSTRAINT_NAME;
        """,
    ).stdout.splitlines()

    assert constraints == [
        "habit|fk_habit_user|FOREIGN KEY",
        "habit|PRIMARY|PRIMARY KEY",
        "habit|uq_habit_id_user|UNIQUE",
        "habit_log|chk_habit_log_duration|CHECK",
        "habit_log|fk_habit_log_habit_owner|FOREIGN KEY",
        "habit_log|fk_habit_log_user|FOREIGN KEY",
        "habit_log|PRIMARY|PRIMARY KEY",
        "user|PRIMARY|PRIMARY KEY",
        "user|uq_user_email|UNIQUE",
        "user|uq_user_username|UNIQUE",
        "habit|fk_habit_user|user|CASCADE|CASCADE",
        "habit_log|fk_habit_log_habit_owner|habit|CASCADE|CASCADE",
        "habit_log|fk_habit_log_user|user|CASCADE|CASCADE",
    ]


def test_database_population(mysql_container: str) -> None:
    """Validate the demo user, habits, and August 2026 completion data."""
    population = run_mysql(
        mysql_container,
        """
        SELECT COUNT(*)
        FROM habitdb.user
        WHERE username = 'demo_user' AND email = 'demo@example.com';

        SELECT GROUP_CONCAT(habit.name ORDER BY habit.name), COUNT(*)
        FROM habitdb.habit AS habit
        JOIN habitdb.user AS owner ON owner.id = habit.id_user
        WHERE owner.username = 'demo_user';

        SELECT MIN(habit_log.log_date), MAX(habit_log.log_date),
               COUNT(*), COUNT(DISTINCT habit_log.id_habit)
        FROM habitdb.habit_log AS habit_log
        JOIN habitdb.user AS owner ON owner.id = habit_log.id_user
        WHERE owner.username = 'demo_user';
        """,
    ).stdout.splitlines()

    assert population[0] == "1"
    assert population[1] == "Dance,Read,Study,Travel,Workout\t5"

    first_date, last_date, log_count, habit_count = population[2].split("\t")
    assert first_date == "2026-08-01"
    assert last_date == "2026-08-31"
    assert int(log_count) > 0
    assert habit_count == "5"

    run_mysql(
        mysql_container,
        "SOURCE /docker-entrypoint-initdb.d/02_data_population.sql;",
    )
    rerun_counts = run_mysql(
        mysql_container,
        """
        SELECT COUNT(*) FROM habitdb.user WHERE username = 'demo_user';
        SELECT COUNT(*)
        FROM habitdb.habit AS habit
        JOIN habitdb.user AS owner ON owner.id = habit.id_user
        WHERE owner.username = 'demo_user';
        SELECT COUNT(*)
        FROM habitdb.habit_log AS habit_log
        JOIN habitdb.user AS owner ON owner.id = habit_log.id_user
        WHERE owner.username = 'demo_user';
        """,
    ).stdout.splitlines()
    assert rerun_counts == ["1", "5", log_count]


def test_database_constraints_and_cascades(mysql_container: str) -> None:
    """Validate uniqueness, ownership integrity, defaults, and cascades."""
    run_mysql(
        mysql_container,
        """
        INSERT INTO habitdb.user (username, email, password)
        VALUES ('test_owner', 'test_owner@example.com', 'hash'),
               ('test_other', 'test_other@example.com', 'hash');
        INSERT INTO habitdb.habit (name, color, description, id_user)
        SELECT 'Test Habit', '#336699', 'Integration test habit', id
        FROM habitdb.user
        WHERE username = 'test_owner';
        INSERT INTO habitdb.habit_log (id_habit, id_user, log_date)
        SELECT id, id_user, '2026-09-03'
        FROM habitdb.habit
        WHERE name = 'Test Habit';
        """,
    )

    duration = run_mysql(
        mysql_container,
        """
        SELECT habit_log.habit_duration
        FROM habitdb.habit_log AS habit_log
        JOIN habitdb.habit AS habit ON habit.id = habit_log.id_habit
        WHERE habit.name = 'Test Habit';
        """,
    ).stdout.strip()
    assert duration == "60"

    invalid_statements = [
        "INSERT INTO habitdb.user (username, email, password) VALUES ('test_owner', 'new@example.com', 'hash');",
        "INSERT INTO habitdb.user (username, email, password) VALUES ('new', 'test_owner@example.com', 'hash');",
        """
        INSERT INTO habitdb.habit_log (id_habit, id_user, log_date)
        SELECT id, id_user, '2026-09-03'
        FROM habitdb.habit WHERE name = 'Test Habit';
        """,
        """
        INSERT INTO habitdb.habit_log (id_habit, id_user, log_date)
        SELECT habit.id, other_user.id, '2026-09-04'
        FROM habitdb.habit AS habit
        JOIN habitdb.user AS other_user ON other_user.username = 'test_other'
        WHERE habit.name = 'Test Habit';
        """,
    ]
    for statement in invalid_statements:
        assert run_mysql(mysql_container, statement, check=False).returncode != 0

    run_mysql(mysql_container, "DELETE FROM habitdb.user WHERE username = 'test_owner';")
    remaining = run_mysql(
        mysql_container,
        """
        SELECT COUNT(*) FROM habitdb.habit WHERE name = 'Test Habit';
        SELECT COUNT(*)
        FROM habitdb.habit_log AS habit_log
        JOIN habitdb.habit AS habit ON habit.id = habit_log.id_habit
        WHERE habit.name = 'Test Habit';
        """,
    ).stdout.splitlines()
    assert remaining == ["0", "0"]