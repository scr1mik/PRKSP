import argparse
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
import uvicorn

from app.core.config import Settings, settings
from app.core.logging import configure_logging, get_logger
from app.core.security import hash_password
from app.db.session import create_session_factory
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate

INITIAL_SCHEMA_REVISION = "20260510_0001"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def build_alembic_config(app_settings: Settings = settings) -> Config:
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", app_settings.database_url)
    return config


def initial_schema_exists_without_alembic(app_settings: Settings) -> bool:
    session_factory = create_session_factory(app_settings.database_url)
    engine = session_factory.kw["bind"]
    try:
        table_names = set(inspect(engine).get_table_names())
        return "alembic_version" not in table_names and {"events", "users"}.issubset(table_names)
    finally:
        engine.dispose()


def migrate_database(app_settings: Settings = settings) -> None:
    alembic_config = build_alembic_config(app_settings)
    if initial_schema_exists_without_alembic(app_settings):
        command.stamp(alembic_config, INITIAL_SCHEMA_REVISION)
        return

    command.upgrade(alembic_config, "head")


def create_admin_user(
    app_settings: Settings = settings,
    *,
    email: str,
    password: str,
    full_name: str,
) -> User:
    migrate_database(app_settings)
    session_factory = create_session_factory(app_settings.database_url)
    with session_factory() as db_session:
        repository = UserRepository(db_session)
        existing_user = repository.get_by_email(email.lower())
        if existing_user is not None:
            return existing_user

        payload = UserCreate(email=email, password=password, full_name=full_name)
        return repository.create(payload, hash_password(password))


def run_server(app_settings: Settings = settings) -> None:
    uvicorn.run(
        "app.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=app_settings.debug,
        access_log=False,
        log_config=None,
        timeout_graceful_shutdown=app_settings.shutdown_timeout_seconds,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Future Events Tracker administrative CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("server", help="Run the FastAPI web server")
    subparsers.add_parser("migrate", help="Apply database schema changes and exit")

    create_admin_parser = subparsers.add_parser(
        "create-admin",
        help="Create an administrator user and exit",
    )
    create_admin_parser.add_argument("--email", required=True)
    create_admin_parser.add_argument("--password", required=True)
    create_admin_parser.add_argument("--full-name", default="Admin User")

    return parser


def main(argv: list[str] | None = None) -> None:
    configure_logging(settings.app_name)
    logger = get_logger()
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "server"

    if command == "server":
        run_server(settings)
        return

    if command == "migrate":
        migrate_database(settings)
        logger.info("database_migration_completed")
        return

    if command == "create-admin":
        user = create_admin_user(
            settings,
            email=args.email,
            password=args.password,
            full_name=args.full_name,
        )
        logger.info(
            "admin_user_ready",
            extra={"structured": {"email": user.email, "user_id": user.id}},
        )
        return

    parser.error(f"Unknown command: {command}")
