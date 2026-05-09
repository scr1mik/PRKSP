import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_request_id_header_and_structured_stdout_log(tmp_path: Path, capsys) -> None:
    database_path = tmp_path / "logging.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}", redis_url="")
    client = TestClient(create_app(settings))

    response = client.get("/health", headers={"X-Request-ID": "report-request-1"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "report-request-1"

    captured = capsys.readouterr()
    log_record = json.loads(captured.out.strip().splitlines()[-1])

    assert log_record["level"] == "info"
    assert log_record["service"] == "Future Events Tracker"
    assert log_record["request_id"] == "report-request-1"
    assert log_record["message"] == "http_request_completed"
    assert log_record["method"] == "GET"
    assert log_record["path"] == "/health"
    assert log_record["status_code"] == 200
    assert "timestamp" in log_record
