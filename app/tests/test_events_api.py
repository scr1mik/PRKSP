from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_event_crud_flow(tmp_path: Path) -> None:
    database_path = tmp_path / "test_events.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}")
    client = TestClient(create_app(settings))

    create_response = client.post(
        "/api/events/",
        json={
            "title": "Новая пандемия 2032",
            "description": "Учебное событие для проверки CRUD-операций в API.",
            "year": 2032,
            "category": "Пандемия",
        },
    )
    assert create_response.status_code == 201
    created_event = create_response.json()
    assert created_event["title"] == "Новая пандемия 2032"

    list_response = client.get("/api/events/")
    assert list_response.status_code == 200
    events = list_response.json()
    assert len(events) == 1

    update_response = client.put(
        f"/api/events/{created_event['id']}",
        json={
            "title": "Вторжение инопланетян",
            "description": "Сценарий обновлен через API для демонстрации редактирования.",
            "year": 2040,
            "category": "Инопланетяне",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["year"] == 2040

    delete_response = client.delete(f"/api/events/{created_event['id']}")
    assert delete_response.status_code == 204

    final_list_response = client.get("/api/events/")
    assert final_list_response.status_code == 200
    assert final_list_response.json() == []


def test_events_persist_across_app_restarts(tmp_path: Path) -> None:
    database_path = tmp_path / "persistent_events.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}")

    first_client = TestClient(create_app(settings))
    create_response = first_client.post(
        "/api/events/",
        json={
            "title": "Сигнал из глубин космоса",
            "description": "Событие должно сохраниться после перезапуска приложения.",
            "year": 2045,
            "category": "Космос",
        },
    )
    assert create_response.status_code == 201

    second_client = TestClient(create_app(settings))
    list_response = second_client.get("/api/events/")

    assert list_response.status_code == 200
    events = list_response.json()
    assert len(events) == 1
    assert events[0]["title"] == "Сигнал из глубин космоса"
