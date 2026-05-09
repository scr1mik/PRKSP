from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.db.base import Base


def initialize_database_schema(engine: Engine) -> None:
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(text("SELECT pg_advisory_lock(5005)"))
            try:
                Base.metadata.create_all(bind=connection)
            finally:
                connection.execute(text("SELECT pg_advisory_unlock(5005)"))
        return

    Base.metadata.create_all(bind=engine)
