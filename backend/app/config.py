"""Configuración centralizada del backend."""

import logging
import secrets
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]

_log = logging.getLogger(__name__)

SUPPORTED_APP_ENVS = frozenset(
    {"development", "dev", "local", "staging", "stage", "production", "prod"}
)
NON_DEV_ENVS = frozenset({"staging", "stage", "production", "prod"})


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
    secret_key: str = Field(default="")
    enable_api_docs: bool = False

    @field_validator("app_env", mode="before")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """Normaliza y valida el entorno antes de aplicar guardas de seguridad."""

        normalized = str(v).strip().lower()
        if normalized not in SUPPORTED_APP_ENVS:
            supported = ", ".join(sorted(SUPPORTED_APP_ENVS))
            raise ValueError(
                f"APP_ENV '{v}' no soportado. Valores válidos: {supported}"
            )
        return normalized

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        """Valida o genera SECRET_KEY según entorno."""
        # Resolver app_env una sola vez; en tests info.data puede ser None
        if info.data:
            app_env_raw = info.data.get("app_env", "development")
        else:
            app_env_raw = "development"
        app_env_normalized = app_env_raw.strip().lower()

        if not v:
            if app_env_normalized in NON_DEV_ENVS:
                raise ValueError(
                    "SECRET_KEY vacío no permitido fuera de desarrollo "
                    "(APP_ENV actual: %s). "
                    "Generá uno con: python -c 'import secrets; print(secrets.token_hex(32))'"
                    % app_env_raw
                )

            v = secrets.token_hex(32)
            _log.warning(
                "SECRET_KEY generado automáticamente para desarrollo (longitud=%d)",
                len(v),
            )
            return v

        if v == "manttoai-dev-secret":
            if app_env_normalized in NON_DEV_ENVS:
                raise ValueError(
                    "SECRET_KEY usa el valor por defecto 'manttoai-dev-secret' "
                    "que no es seguro para producción (APP_ENV actual: %s). "
                    "Configurá SECRET_KEY en .env o secrets manager." % app_env_raw
                )

            _log.warning(
                "SECRET_KEY usa el valor por defecto obsoleto "
                "'manttoai-dev-secret'. Generá uno propio con: "
                "python -c 'import secrets; print(secrets.token_hex(32))'"
            )

        return v

    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
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
    # Días de telemetría a conservar; 0 deshabilita la purga automática.
    telemetry_retention_days: int = Field(default=0, ge=0, le=3650)
    auth_cookie_name: str = "manttoai_token"
    auth_csrf_cookie_name: str = "manttoai_csrf"
    auth_csrf_header_name: str = "X-CSRF-Token"
    # Redis (rate limiting + caché opcional de revocación JWT)
    # Vacío significa fallback explícito a memoria para rate limiting; la
    # revocación persistente vive en MySQL y no depende de Redis.
    redis_url: str = ""
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
    # Redes/IPs de reverse proxies autorizados a enviar X-Forwarded-For.
    trusted_proxy_ips: str = ""

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

        app_env_normalized = self.app_env.strip().lower()
        database_url_normalized = self.database_url.strip().lower()

        if app_env_normalized in NON_DEV_ENVS:
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

        if app_env_normalized in NON_DEV_ENVS and self.mqtt_enabled:
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

        if app_env_normalized in NON_DEV_ENVS and self.smtp_require_auth:
            if not self.smtp_user or not self.smtp_password:
                raise ValueError(
                    "SMTP requiere autenticación fuera de desarrollo, pero faltan "
                    "SMTP_USER o SMTP_PASSWORD en backend/.env"
                )

        if app_env_normalized in NON_DEV_ENVS and self.smtp_host:
            if not self.smtp_from_email or not self.smtp_to_email:
                raise ValueError(
                    "SMTP está configurado fuera de desarrollo pero faltan "
                    "SMTP_FROM_EMAIL o SMTP_TO_EMAIL en backend/.env"
                )

        if app_env_normalized in NON_DEV_ENVS and "*" in self.get_cors_origins():
            raise ValueError(
                "CORS_ALLOWED_ORIGINS wildcard no permitido fuera de desarrollo "
                "cuando la API usa cookies"
            )

        if (
            app_env_normalized in NON_DEV_ENVS
            and self.redis_url.strip()
            and not self.redis_password
        ):
            _log.warning(
                "REDIS_PASSWORD no está definido. "
                "Si REDIS_URL requiere autenticación, rate limiting y JWT "
                "blacklist usarán el fallback en memoria."
            )

        return self


@lru_cache
def get_settings() -> Settings:
    """Entrega una instancia cacheada de configuración."""

    return Settings()


def get_redis_connection_kwargs(settings: Settings | None = None) -> dict[str, str]:
    """Entrega credenciales Redis separadas sin sobrescribir las de la URL."""

    resolved_settings = settings or get_settings()
    redis_url = resolved_settings.redis_url.strip()
    password = resolved_settings.redis_password.strip()
    if not redis_url or not password:
        return {}

    try:
        url_has_password = bool(urlparse(redis_url).password)
    except ValueError:
        url_has_password = False

    if url_has_password:
        return {}

    return {"password": password}
