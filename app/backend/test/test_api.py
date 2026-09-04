"""MySQL-backed integration tests for authenticated Habit Tracker API routes."""

from __future__ import annotations

import os
import subprocess
import time
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


DATABASE_DIRECTORY = Path(__file__).resolve().parents[2] / "database"
TEST_ROOT_PASSWORD = "backend-test-root-password"
TEST_JWT_SECRET = "backend-test-jwt-secret-that-is-long-enough"


def run_command(*command: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command and capture text output.

    Args:
        *command: Executable and command-line arguments.
        check: Whether a non-zero status raises an exception.

    Returns:
        Completed process with captured output.
    """
    return subprocess.run(command, check=check, capture_output=True, text=True)


@pytest.fixture(scope="module")
def api_client() -> Iterator[TestClient]:
    """Provide an API client connected to a disposable initialized MySQL image.

    Yields:
        FastAPI client configured with a temporary MySQL database URL.
    """
    docker_status = run_command("docker", "info", check=False)
    if docker_status.returncode != 0:
        pytest.skip(f"Docker is unavailable: {docker_status.stderr.strip()}")

    suffix = uuid.uuid4().hex[:12]
    image_name = f"habitdb-backend-test:{suffix}"
    container_name = f"habitdb-backend-test-{suffix}"
    try:
        run_command("docker", "build", "--tag", image_name, str(DATABASE_DIRECTORY))
        run_command(
            "docker",
            "run",
            "--detach",
            "--name",
            container_name,
            "--publish",
            "127.0.0.1::3306",
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

        port = run_command("docker", "port", container_name, "3306/tcp").stdout.strip().rsplit(":", 1)[1]
        os.environ["DATABASE_URL"] = f"mysql+pymysql://root:{TEST_ROOT_PASSWORD}@127.0.0.1:{port}/habitdb"
        os.environ["JWT_SECRET_KEY"] = TEST_JWT_SECRET
        from app.backend.src.app import app

        with TestClient(app) as client:
            yield client
    finally:
        os.environ.pop("DATABASE_URL", None)
        os.environ.pop("JWT_SECRET_KEY", None)
        run_command("docker", "rm", "--force", container_name, check=False)
        run_command("docker", "image", "rm", "--force", image_name, check=False)


def register_and_login(api_client: TestClient, username: str, email: str) -> tuple[int, dict[str, str]]:
    """Register a user and return their identifier and bearer headers.

    Args:
        api_client: Configured API test client.
        username: Unique username for the test account.
        email: Unique email for the test account.

    Returns:
        User identifier and authorization headers.
    """
    password = "correct-horse-battery-staple"
    registration = api_client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert registration.status_code == 201
    assert "password" not in registration.json()
    login = api_client.post("/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200
    return registration.json()["id"], {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_registration_login_and_profile(api_client: TestClient) -> None:
    """Register, authenticate, and retrieve a private user profile."""
    user_id, headers = register_and_login(api_client, "api_owner", "api_owner@example.com")

    assert api_client.post("/auth/login", json={"username": "api_owner", "password": "wrong-password"}).status_code == 401
    assert api_client.get(f"/users/{user_id}").status_code == 401
    profile = api_client.get(f"/users/{user_id}", headers=headers)
    assert profile.status_code == 200
    assert profile.json() == {"id": user_id, "username": "api_owner", "email": "api_owner@example.com"}
    duplicate = api_client.post(
        "/auth/register",
        json={"username": "api_owner", "email": "different@example.com", "password": "correct-horse-battery-staple"},
    )
    assert duplicate.status_code == 409
    assert api_client.get(f"/users/{user_id}", headers={"Authorization": "Bearer invalid-token"}).status_code == 401


def test_habit_and_log_crud_are_owner_scoped(api_client: TestClient) -> None:
    """Create, modify, upsert, and delete resources owned by one user."""
    user_id, headers = register_and_login(api_client, "habit_owner", "habit_owner@example.com")
    created_habit = api_client.post(
        f"/users/{user_id}/habits",
        headers=headers,
        json={"name": "Read", "color": "#123456", "description": "Daily reading"},
    )
    assert created_habit.status_code == 201
    habit_id = created_habit.json()["id"]
    assert api_client.get(f"/users/{user_id}/habits", headers=headers).json()[0]["id"] == habit_id
    assert api_client.patch(f"/habits/{habit_id}", headers=headers, json={"description": "Evening reading"}).json()["description"] == "Evening reading"

    first_log = api_client.post(
        f"/habits/{habit_id}/logs",
        headers=headers,
        json={"log_date": "2026-09-04"},
    )
    assert first_log.status_code == 201
    assert first_log.json()["habit_duration"] == 60
    updated_log = api_client.post(
        f"/habits/{habit_id}/logs",
        headers=headers,
        json={"log_date": "2026-09-04", "habit_duration": 45},
    )
    assert updated_log.status_code == 200
    assert updated_log.json()["habit_duration"] == 45
    assert api_client.patch(
        f"/habits/{habit_id}/logs/2026-09-04",
        headers=headers,
        json={"habit_duration": 30},
    ).json()["habit_duration"] == 30
    assert api_client.post(
        f"/habits/{habit_id}/logs",
        headers=headers,
        json={"log_date": "2026-09-05", "habit_duration": -1},
    ).status_code == 422
    assert api_client.delete(f"/habits/{habit_id}/logs/2026-09-04", headers=headers).status_code == 204
    assert api_client.delete(f"/habits/{habit_id}", headers=headers).status_code == 204


def test_cross_user_access_is_rejected(api_client: TestClient) -> None:
    """Prevent one authenticated user from accessing another user's resources."""
    owner_id, owner_headers = register_and_login(api_client, "first_owner", "first_owner@example.com")
    other_id, other_headers = register_and_login(api_client, "second_owner", "second_owner@example.com")
    habit = api_client.post(
        f"/users/{owner_id}/habits",
        headers=owner_headers,
        json={"name": "Private habit", "color": "#654321"},
    )
    habit_id = habit.json()["id"]

    assert api_client.get(f"/users/{owner_id}/habits", headers=other_headers).status_code == 403
    assert api_client.get(f"/habits/{habit_id}", headers=other_headers).status_code == 404
    assert api_client.get(f"/users/{other_id}", headers=owner_headers).status_code == 403


def test_profile_updates_and_deletion_cascade(api_client: TestClient) -> None:
    """Update a self profile and confirm account deletion removes owned data."""
    user_id, headers = register_and_login(api_client, "cascade_owner", "cascade_owner@example.com")
    updated_profile = api_client.patch(
        f"/users/{user_id}",
        headers=headers,
        json={"email": "cascade_owner_updated@example.com"},
    )
    assert updated_profile.status_code == 200
    assert updated_profile.json()["email"] == "cascade_owner_updated@example.com"
    habit = api_client.post(
        f"/users/{user_id}/habits",
        headers=headers,
        json={"name": "Cascade habit", "color": "#456789"},
    )
    habit_id = habit.json()["id"]
    assert api_client.post(
        f"/habits/{habit_id}/logs",
        headers=headers,
        json={"log_date": "2026-09-06", "habit_duration": 15},
    ).status_code == 201

    assert api_client.delete(f"/users/{user_id}", headers=headers).status_code == 204
    assert api_client.get(f"/users/{user_id}", headers=headers).status_code == 404
    assert api_client.get(f"/habits/{habit_id}", headers=headers).status_code == 404