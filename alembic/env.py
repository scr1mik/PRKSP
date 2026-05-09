from logging.config import fileConfig

from sqlalchemy import engine_from_config, inspect, pool, text

from alembic import context
from app.core.config import settings
from app.db.base import Base
from app.models.event import Event  # noqa: F401
from app.models.user import User  # noqa: F401

config = context.config
INITIAL_SCHEMA_REVISION = "20260510_0001"

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def get_database_url() -> str:
    configured_url = config.get_main_option("sqlalchemy.url")
    if configured_url and configured_url != "sqlite:///./events.db":
        return configured_url
    return settings.database_url


def legacy_schema_needs_stamp(connection, table_names: set[str]) -> bool:
    if not {"events", "users"}.issubset(table_names):
        return False

    if "alembic_version" not in table_names:
        return True

    version = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
    return version is None


def stamp_initial_schema(connection, table_names: set[str]) -> None:
    if "alembic_version" not in table_names:
        connection.execute(
            text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
        )

    connection.execute(text("DELETE FROM alembic_version"))
    connection.execute(
        text("INSERT INTO alembic_version (version_num) VALUES (:revision)"),
        {"revision": INITIAL_SCHEMA_REVISION},
    )
    connection.commit()


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        table_names = set(inspect(connection).get_table_names())
        if legacy_schema_needs_stamp(connection, table_names):
            stamp_initial_schema(connection, table_names)

        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()
        connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
