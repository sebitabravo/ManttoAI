"""Configuración centralizada del backend."""

from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Representa las variables de entorno de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ManttoAI Predictive Maintenance API"
    app_env: str = "development"
    api_prefix: str = ""
    database_url: str = "sqlite:///./manttoai.db"
    database_auto_init: bool = True
    secret_key: str = "manttoai-dev-secret"
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_base_topic: str = "manttoai/equipo"
    mqtt_enabled: bool = True
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_to_email: str = ""
    enable_prediction_scheduler: bool = True
    prediction_interval_seconds: int = 300

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        """Valida mínimos de seguridad según entorno configurado."""

        non_dev_envs = {"staging", "stage", "production", "prod"}
        app_env_normalized = self.app_env.strip().lower()
        if (
            app_env_normalized in non_dev_envs
            and self.secret_key == "manttoai-dev-secret"
        ):
            raise ValueError("SECRET_KEY por defecto no permitido fuera de desarrollo")

        return self


@lru_cache
def get_settings() -> Settings:
    """Entrega una instancia cacheada de configuración."""

    return Settings()
