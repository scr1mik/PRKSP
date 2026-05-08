import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        super().__init__(settings_cls)
        config_file = Path(os.getenv("APP_CONFIG_FILE", "config/local.yaml"))
        self.yaml_data = self._load_yaml_data(config_file)

    @staticmethod
    def _load_yaml_data(config_file: Path) -> dict[str, Any]:
        if not config_file.exists():
            return {}

        with config_file.open("r", encoding="utf-8") as yaml_file:
            raw_data = yaml.safe_load(yaml_file) or {}

        if not isinstance(raw_data, dict):
            return {}

        return raw_data

    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        value = self.yaml_data.get(field_name)
        return value, field_name, False

    def __call__(self) -> dict[str, Any]:
        return self.yaml_data


class Settings(BaseSettings):
    app_name: str = "Future Events Tracker"
    app_version: str = "0.1.0"
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    database_url: str = "sqlite:///./events.db"
    frontend_origin: str = "http://localhost:5173"
    api_prefix: str = "/api"
    debug: bool = True
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug_value(cls, value: Any) -> bool:
        if isinstance(value, bool):
            return value

        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug", "development"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "production"}:
            return False
        return bool(value)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )


settings = Settings()
