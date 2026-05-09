from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import Engine
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import Settings, settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import create_session_factory
from app.middleware import request_logging_middleware
from app.models.event import Event
from app.models.user import User
from app.services.session_store import create_session_store


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


def create_app(app_settings: Settings = settings) -> FastAPI:
    configure_logging(app_settings.app_name)
    app = FastAPI(title=app_settings.app_name, version=app_settings.app_version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_logging_middleware)

    session_factory = create_session_factory(app_settings.database_url)
    initialize_database_schema(session_factory.kw["bind"])
    app.state.settings = app_settings
    app.state.session_factory = session_factory
    app.state.session_store = create_session_store(app_settings.redis_url)

    app.include_router(api_router, prefix=app_settings.api_prefix)

    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        assets_dir = frontend_dist / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/", include_in_schema=False)
        def serve_frontend() -> FileResponse:
            return FileResponse(frontend_dist / "index.html")
    else:
        @app.get("/", include_in_schema=False)
        def root_info() -> JSONResponse:
            return JSONResponse(
                {
                    "service": app_settings.app_name,
                    "docs": "/docs",
                    "health": "/health",
                }
            )

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        with session_factory() as db_session:
            db_session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}

    return app


app = create_app()
