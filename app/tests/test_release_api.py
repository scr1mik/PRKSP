from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_release_endpoint_reports_image_and_environment(tmp_path: Path) -> None:
    database_path = tmp_path / "release.db"
    settings = Settings(
        sqlite_url=f"sqlite:///{database_path}",
        app_env="staging",
        image_tag="sha-abc123",
        release_id="run-42",
    )
    client = TestClient(create_app(settings))

    response = client.get("/api/release")

    assert response.status_code == 200
    assert response.json() == {
        "service": "Future Events Tracker",
        "version": "0.1.0",
        "environment": "staging",
        "image_tag": "sha-abc123",
        "release_id": "run-42",
    }
