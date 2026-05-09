from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_new_requests_are_rejected_during_shutdown(tmp_path: Path) -> None:
    database_path = tmp_path / "shutdown.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}", redis_url="")
    app = create_app(settings)
    app.state.is_shutting_down = True
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "Service is shutting down"}


def test_readiness_reports_shutdown_state(tmp_path: Path) -> None:
    database_path = tmp_path / "readiness.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}", redis_url="")
    app = create_app(settings)
    client = TestClient(app)

    ready_response = client.get("/ready")
    assert ready_response.status_code == 200
    assert ready_response.json() == {"status": "ready"}

    app.state.is_shutting_down = True
    shutdown_response = client.get("/ready")

    assert shutdown_response.status_code == 503
    assert shutdown_response.json() == {"detail": "Service is shutting down"}


def test_slow_runtime_endpoint_finishes_successfully(tmp_path: Path) -> None:
    database_path = tmp_path / "slow.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}", redis_url="")
    client = TestClient(create_app(settings))

    response = client.get("/api/runtime/slow?seconds=0")

    assert response.status_code == 200
    assert response.json() == {"status": "completed", "seconds": 0.0}
