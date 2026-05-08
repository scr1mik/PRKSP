from pathlib import Path

import yaml

from app.core.config import Settings


def test_environment_variables_override_yaml(tmp_path: Path, monkeypatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    yaml_path = config_dir / "local.yaml"
    yaml_path.write_text(
        yaml.safe_dump(
            {
                "port": 7000,
                "app_env": "yaml",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("APP_CONFIG_FILE", str(yaml_path))
    monkeypatch.setenv("PORT", "5050")
    monkeypatch.setenv("APP_ENV", "staging")

    loaded_settings = Settings()

    assert loaded_settings.port == 5050
    assert loaded_settings.app_env == "staging"
    assert loaded_settings.database_url == "sqlite:///./events.db"
