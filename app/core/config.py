from dataclasses import dataclass, field


@dataclass(slots=True)
class Settings:
    app_name: str = "Future Events Tracker"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./events.db"
    frontend_origin: str = "http://localhost:5173"
    api_prefix: str = "/api"
    debug: bool = True
    allowed_origins: list[str] = field(default_factory=lambda: ["http://localhost:5173"])


settings = Settings()
