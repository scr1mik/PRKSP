from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_user_session_flow_uses_shared_session_store(tmp_path: Path) -> None:
    database_path = tmp_path / "auth.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}", redis_url="")
    client = TestClient(create_app(settings))

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "student@example.com",
            "password": "strong-password",
            "full_name": "Student User",
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "student@example.com"
    assert "password" not in register_response.text

    login_response = client.post(
        "/api/auth/login",
        json={"email": "student@example.com", "password": "strong-password"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["email"] == "student@example.com"
    assert "session_id" in client.cookies

    me_response = client.get("/api/auth/me")

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "student@example.com"

    logout_response = client.post("/api/auth/logout")

    assert logout_response.status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_duplicate_user_registration_is_rejected(tmp_path: Path) -> None:
    database_path = tmp_path / "duplicate_auth.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}", redis_url="")
    client = TestClient(create_app(settings))
    payload = {
        "email": "student@example.com",
        "password": "strong-password",
        "full_name": "Student User",
    }

    assert client.post("/api/auth/register", json=payload).status_code == 201
    duplicate_response = client.post("/api/auth/register", json=payload)

    assert duplicate_response.status_code == 409
