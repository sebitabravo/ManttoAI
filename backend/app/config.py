"""Configuración centralizada del backend."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
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
    # SECRET_KEY no tiene default — debe definirse en .env.
    # En desarrollo usar: openssl rand -hex 32
    secret_key: str = Field(default="manttoai-dev-secret")
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_base_topic: str = "manttoai/equipo"
    mqtt_enabled: bool = True
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_to_email: str = ""
    smtp_use_ssl: bool = False
    smtp_timeout: int = 10
    smtp_retry_attempts: int = 3
    smtp_retry_backoff: float = 0.5
    enable_prediction_scheduler: bool = True
    prediction_interval_seconds: int = 300
    prediction_scheduler_max_workers: int = 4
    auth_cookie_name: str = "manttoai_token"
    auth_csrf_cookie_name: str = "manttoai_csrf"
    auth_csrf_header_name: str = "X-CSRF-Token"
    # Orígenes CORS permitidos separados por coma.
    # En desarrollo: localhost:5173. En producción: dominio real del frontend.
    # Ejemplo: CORS_ALLOWED_ORIGINS=https://manttoai.ejemplo.com,https://www.manttoai.ejemplo.com
    cors_allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    def get_cors_origins(self) -> list[str]:
        """Parsea la lista de orígenes CORS desde la variable de entorno."""

        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        """Valida mínimos de seguridad según entorno configurado."""

        import logging

        _log = logging.getLogger(__name__)

        non_dev_envs = {"staging", "stage", "production", "prod"}
        app_env_normalized = self.app_env.strip().lower()

        if self.secret_key == "manttoai-dev-secret":
            if app_env_normalized in non_dev_envs:
                raise ValueError(
                    "SECRET_KEY por defecto no permitido fuera de desarrollo. "
                    "Generá una clave segura con: openssl rand -hex 32"
                )
            # Advertencia en desarrollo para que el equipo no olvide cambiarla
            _log.warning(
                "SECRET_KEY usa el valor por defecto de desarrollo. "
                "Definí SECRET_KEY en backend/.env antes de desplegar."
            )

        return self


@lru_cache
def get_settings() -> Settings:
    """Entrega una instancia cacheada de configuración."""

    return Settings()
