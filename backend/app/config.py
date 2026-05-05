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

    app_name: str = "ManttoAI — Monitoreo IoT por Rubro API"
    app_env: str = "development"
    api_prefix: str = ""
    database_url: str = "sqlite:///./manttoai.db"
    database_auto_init: bool = True
    # En desarrollo se permite fallback para facilitar demo local.
    # En stage/prod se exige valor seguro (ver validate_security_settings).
    secret_key: str = Field(default="manttoai-dev-secret")
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_base_topic: str = "manttoai/telemetria"
    mqtt_telemetry_topic: str = "manttoai/telemetria"
    mqtt_enabled: bool = True
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_to_email: str = ""
    smtp_use_ssl: bool = False
    smtp_use_starttls: bool = True
    smtp_require_auth: bool = False
    smtp_timeout: int = 10
    smtp_retry_attempts: int = 3
    smtp_retry_backoff: float = 0.5
    enable_prediction_scheduler: bool = True
    prediction_interval_seconds: int = 30
    prediction_scheduler_max_workers: int = 4
    ml_auto_train_on_missing: bool = True
    # Simulador de sensores IoT para demo (genera lecturas MQTT automáticas)
    simulator_enabled: bool = False
    simulator_interval_seconds: int = 30
    auth_cookie_name: str = "manttoai_token"
    auth_csrf_cookie_name: str = "manttoai_csrf"
    auth_csrf_header_name: str = "X-CSRF-Token"
    # Redis (rate limiting + JWT blacklist)
    redis_url: str = "redis://redis:6379"
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = ""
    # Integración con Ollama
    ollama_url: str = "http://ollama:11434"
    ollama_model: str = "qwen2.5:0.5b"
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
        database_url_normalized = self.database_url.strip().lower()

        if not self.secret_key or self.secret_key == "manttoai-dev-secret":
            if app_env_normalized in non_dev_envs:
                raise ValueError(
                    "SECRET_KEY vacío o por defecto no permitido fuera de desarrollo. "
                    "Generá una clave segura con: openssl rand -hex 32"
                )
            # Advertencia en desarrollo para que el equipo no olvide cambiarla
            _log.warning(
                "SECRET_KEY usa valor por defecto o está vacío en desarrollo. "
                "Definí SECRET_KEY en backend/.env antes de desplegar."
            )

        if app_env_normalized in non_dev_envs:
            if database_url_normalized.startswith("sqlite"):
                raise ValueError(
                    "DATABASE_URL usa SQLite. No se permite SQLite fuera de desarrollo. "
                    "Definí DATABASE_URL apuntando a MySQL antes de desplegar."
                )

            if "manttoai_root" in database_url_normalized:
                raise ValueError(
                    "DATABASE_URL usa credenciales demo por defecto. "
                    "Definí credenciales reales antes de desplegar fuera de desarrollo."
                )

        if app_env_normalized in non_dev_envs and self.mqtt_enabled:
            if not self.mqtt_username or not self.mqtt_password:
                raise ValueError(
                    "MQTT está habilitado fuera de desarrollo pero faltan credenciales "
                    "(MQTT_USERNAME o MQTT_PASSWORD). Definí ambas en backend/.env"
                )

            if self.mqtt_password == "manttoai_mqtt_dev":
                raise ValueError(
                    "MQTT_PASSWORD por defecto no permitido fuera de desarrollo. "
                    "Definí una contraseña MQTT segura antes de desplegar."
                )

        if app_env_normalized in non_dev_envs and self.smtp_require_auth:
            if not self.smtp_user or not self.smtp_password:
                raise ValueError(
                    "SMTP requiere autenticación fuera de desarrollo, pero faltan "
                    "SMTP_USER o SMTP_PASSWORD en backend/.env"
                )

        if app_env_normalized in non_dev_envs and self.smtp_host:
            if not self.smtp_from_email or not self.smtp_to_email:
                raise ValueError(
                    "SMTP está configurado fuera de desarrollo pero faltan "
                    "SMTP_FROM_EMAIL o SMTP_TO_EMAIL en backend/.env"
                )

        if app_env_normalized in non_dev_envs and not self.redis_password:
            _log.warning(
                "REDIS_PASSWORD no está definido. "
                "Rate limiting y JWT blacklist usarán memoria local. "
                "Definí REDIS_PASSWORD en backend/.env antes de producción."
            )

        return self


@lru_cache
def get_settings() -> Settings:
    """Entrega una instancia cacheada de configuración."""

    return Settings()
