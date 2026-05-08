from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate, EventRead, EventUpdate
from app.services.event_service import EventService

router = APIRouter()


def get_event_service(db_session: Session = Depends(get_db_session)) -> EventService:
    repository = EventRepository(db_session)
    return EventService(repository)


@router.get("/", response_model=list[EventRead])
def list_events(service: EventService = Depends(get_event_service)) -> list[EventRead]:
    return service.list_events()


@router.post("/", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    service: EventService = Depends(get_event_service),
) -> EventRead:
    return service.create_event(payload)


@router.put("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    payload: EventUpdate,
    service: EventService = Depends(get_event_service),
) -> EventRead:
    event = service.update_event(event_id, payload)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    service: EventService = Depends(get_event_service),
) -> Response:
    deleted = service.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
