from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi import Request

from app.core.config import settings


def create_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    engine = create_engine(
        database_url or settings.database_url,
        connect_args={"check_same_thread": False}
        if (database_url or settings.database_url).startswith("sqlite")
        else {},
    )
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


SessionLocal = create_session_factory()


def get_db_session(request: Request) -> Generator[Session, None, None]:
    session_factory: sessionmaker[Session] = getattr(request.app.state, "session_factory", SessionLocal)
    db_session = session_factory()
    try:
        yield db_session
    finally:
        db_session.close()
