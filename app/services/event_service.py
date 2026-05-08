from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate, EventUpdate


class EventService:
    def __init__(self, repository: EventRepository) -> None:
        self.repository = repository

    def list_events(self) -> list[Event]:
        return self.repository.list()

    def create_event(self, payload: EventCreate) -> Event:
        return self.repository.create(payload)

    def update_event(self, event_id: int, payload: EventUpdate) -> Event | None:
        event = self.repository.get(event_id)
        if event is None:
            return None
        return self.repository.update(event, payload)

    def delete_event(self, event_id: int) -> bool:
        event = self.repository.get(event_id)
        if event is None:
            return False
        self.repository.delete(event)
        return True
