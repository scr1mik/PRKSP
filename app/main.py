from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import Settings, settings
from app.db.base import Base
from app.db.session import create_session_factory
from app.models.event import Event


def create_app(app_settings: Settings = settings) -> FastAPI:
    app = FastAPI(title=app_settings.app_name, version=app_settings.app_version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    session_factory = create_session_factory(app_settings.database_url)
    Base.metadata.create_all(bind=session_factory.kw["bind"])
    app.state.session_factory = session_factory

    app.include_router(api_router, prefix=app_settings.api_prefix)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
