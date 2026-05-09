from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_instance_endpoint_reports_process_identity(tmp_path: Path) -> None:
    database_path = tmp_path / "instance.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}")
    client = TestClient(create_app(settings))

    response = client.get("/api/instance")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "Future Events Tracker"
    assert payload["hostname"]
    assert isinstance(payload["pid"], int)
