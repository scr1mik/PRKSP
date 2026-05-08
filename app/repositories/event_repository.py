from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate


class EventRepository:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def list(self) -> list[Event]:
        query = select(Event).order_by(Event.year.asc(), Event.id.asc())
        return list(self.db_session.scalars(query).all())

    def get(self, event_id: int) -> Event | None:
        return self.db_session.get(Event, event_id)

    def create(self, payload: EventCreate) -> Event:
        event = Event(**payload.model_dump())
        self.db_session.add(event)
        self.db_session.commit()
        self.db_session.refresh(event)
        return event

    def update(self, event: Event, payload: EventUpdate) -> Event:
        for field_name, value in payload.model_dump().items():
            setattr(event, field_name, value)
        self.db_session.commit()
        self.db_session.refresh(event)
        return event

    def delete(self, event: Event) -> None:
        self.db_session.delete(event)
        self.db_session.commit()
