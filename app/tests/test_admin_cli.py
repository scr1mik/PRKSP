from pathlib import Path

from alembic import command
from sqlalchemy import text

from app.cli import build_alembic_config, create_admin_user, migrate_database
from app.core.config import Settings
from app.db.base import Base
from app.db.session import create_session_factory
from app.models.event import Event  # noqa: F401
from app.models.user import User


def test_migrate_database_creates_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "admin_migrate.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}", redis_url="")

    migrate_database(settings)

    session_factory = create_session_factory(settings.database_url)
    with session_factory() as db_session:
        assert db_session.query(User).count() == 0
        revision = db_session.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert revision == "20260510_0001"


def test_direct_alembic_upgrade_stamps_legacy_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "legacy_schema.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}", redis_url="")
    session_factory = create_session_factory(settings.database_url)
    engine = session_factory.kw["bind"]
    Base.metadata.create_all(bind=engine)
    engine.dispose()

    command.upgrade(build_alembic_config(settings), "head")

    session_factory = create_session_factory(settings.database_url)
    with session_factory() as db_session:
        revision = db_session.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert revision == "20260510_0001"


def test_direct_alembic_upgrade_handles_partial_legacy_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "partial_legacy_schema.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}", redis_url="")
    session_factory = create_session_factory(settings.database_url)
    engine = session_factory.kw["bind"]
    Event.__table__.create(bind=engine)
    engine.dispose()

    command.upgrade(build_alembic_config(settings), "head")

    session_factory = create_session_factory(settings.database_url)
    with session_factory() as db_session:
        revision = db_session.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        assert revision == "20260510_0001"
        assert db_session.query(User).count() == 0


def test_create_admin_user_is_idempotent(tmp_path: Path) -> None:
    database_path = tmp_path / "admin_user.db"
    settings = Settings(sqlite_url=f"sqlite:///{database_path}", redis_url="")

    first_user = create_admin_user(
        settings,
        email="admin@example.com",
        password="admin-password",
        full_name="Admin User",
    )
    second_user = create_admin_user(
        settings,
        email="admin@example.com",
        password="admin-password",
        full_name="Admin User",
    )

    assert first_user.email == "admin@example.com"
    assert second_user.id == first_user.id

    session_factory = create_session_factory(settings.database_url)
    with session_factory() as db_session:
        assert db_session.query(User).count() == 1
