"""Tests de validación de seguridad para settings."""

import pytest

from app.config import Settings


def test_settings_rejects_default_secret_key_outside_development():
    """No permite SECRET_KEY por defecto en entorno productivo."""

    with pytest.raises(ValueError, match="SECRET_KEY vacío o por defecto"):
        Settings(
            _env_file=None,
            app_env="production",
            secret_key="manttoai-dev-secret",
        )


def test_settings_rejects_empty_secret_key_outside_development():
    """No permite SECRET_KEY vacío fuera de desarrollo."""

    with pytest.raises(ValueError, match="SECRET_KEY vacío o por defecto"):
        Settings(_env_file=None, app_env="production", secret_key="")


def test_settings_rejects_default_database_credentials_outside_development():
    """Bloquea DATABASE_URL con credenciales demo en producción."""

    with pytest.raises(ValueError, match="DATABASE_URL usa credenciales demo"):
        Settings(
            _env_file=None,
            app_env="production",
            secret_key="super-secret-key",
            database_url="mysql+pymysql://root:manttoai_root@mysql:3306/manttoai_db",
            mqtt_enabled=False,
        )


def test_settings_rejects_sqlite_database_outside_development():
    """No permite SQLite en stage/prod para evitar despliegues inseguros."""

    with pytest.raises(ValueError, match="DATABASE_URL usa SQLite"):
        Settings(
            _env_file=None,
            app_env="production",
            secret_key="super-secret-key",
            database_url="sqlite:///./manttoai.db",
            mqtt_enabled=False,
            smtp_host="",
        )


def test_settings_rejects_default_mqtt_password_outside_development():
    """Bloquea MQTT_PASSWORD de demo en stage/prod."""

    with pytest.raises(ValueError, match="MQTT_PASSWORD por defecto"):
        Settings(
            _env_file=None,
            app_env="production",
            secret_key="super-secret-key",
            database_url="mysql+pymysql://root:strong-pass@mysql:3306/manttoai_db",
            mqtt_username="manttoai_mqtt",
            mqtt_password="manttoai_mqtt_dev",
            smtp_host="",
        )


def test_settings_rejects_missing_mqtt_credentials_when_enabled_outside_development():
    """No permite mqtt enabled sin username/password fuera de desarrollo."""

    with pytest.raises(ValueError, match="MQTT está habilitado fuera de desarrollo"):
        Settings(
            _env_file=None,
            app_env="production",
            secret_key="super-secret-key",
            database_url="mysql+pymysql://root:strong-pass@mysql:3306/manttoai_db",
            mqtt_enabled=True,
            mqtt_username="",
            mqtt_password="",
            smtp_host="",
        )


def test_settings_rejects_missing_smtp_auth_credentials_when_required():
    """No permite SMTP auth sin credenciales fuera de desarrollo."""

    with pytest.raises(
        ValueError, match="SMTP requiere autenticación fuera de desarrollo"
    ):
        Settings(
            _env_file=None,
            app_env="production",
            secret_key="super-secret-key",
            database_url="mysql+pymysql://root:strong-pass@mysql:3306/manttoai_db",
            mqtt_enabled=False,
            smtp_host="smtp.example.com",
            smtp_require_auth=True,
            smtp_user="",
            smtp_password="",
            smtp_from_email="noreply@example.com",
            smtp_to_email="alerts@example.com",
        )


def test_settings_rejects_missing_smtp_addresses_when_host_configured():
    """No permite SMTP host sin from/to fuera de desarrollo."""

    with pytest.raises(ValueError, match="SMTP está configurado fuera de desarrollo"):
        Settings(
            _env_file=None,
            app_env="production",
            secret_key="super-secret-key",
            database_url="mysql+pymysql://root:strong-pass@mysql:3306/manttoai_db",
            mqtt_enabled=False,
            smtp_host="smtp.example.com",
            smtp_require_auth=False,
            smtp_from_email="",
            smtp_to_email="",
        )


def test_settings_allows_non_dev_when_credentials_are_explicit():
    """Acepta configuración no-dev cuando las credenciales son seguras y completas."""

    settings = Settings(
        _env_file=None,
        app_env="production",
        secret_key="super-secret-key",
        database_url="mysql+pymysql://root:strong-pass@mysql:3306/manttoai_db",
        mqtt_enabled=True,
        mqtt_username="manttoai_prod",
        mqtt_password="strong-mqtt-pass",
        smtp_host="smtp.example.com",
        smtp_require_auth=True,
        smtp_user="mailer@example.com",
        smtp_password="strong-smtp-pass",
        smtp_from_email="noreply@example.com",
        smtp_to_email="alerts@example.com",
    )

    assert settings.app_env == "production"


def test_settings_allows_defaults_in_development():
    """En development permite defaults para demo local controlada."""

    settings = Settings(
        _env_file=None,
        app_env="development",
        secret_key="manttoai-dev-secret",
        database_url="mysql+pymysql://root:manttoai_root@mysql:3306/manttoai_db",
        mqtt_password="manttoai_mqtt_dev",
    )

    assert settings.app_env == "development"
