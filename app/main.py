from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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
        return {"status": "ok"}

    return app


app = create_app()
