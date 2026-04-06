"""Tests del servicio de email."""

from types import SimpleNamespace

from app.services import email_service


def _build_smtp_settings(
    smtp_host: str = "smtp.example.com",
    smtp_port: int = 587,
    smtp_user: str = "bot@example.com",
    smtp_password: str = "super-secret",
    smtp_from_email: str = "bot@example.com",
    smtp_to_email: str = "alertas@example.com",
    smtp_use_ssl: bool = False,
    smtp_timeout: int = 10,
    smtp_retry_attempts: int = 3,
    smtp_retry_backoff: float = 2.0,
) -> SimpleNamespace:
    """Construye settings SMTP para pruebas unitarias."""

    return SimpleNamespace(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        smtp_from_email=smtp_from_email,
        smtp_to_email=smtp_to_email,
        smtp_use_ssl=smtp_use_ssl,
        smtp_timeout=smtp_timeout,
        smtp_retry_attempts=smtp_retry_attempts,
        smtp_retry_backoff=smtp_retry_backoff,
    )


def test_send_alert_email_uses_mocked_smtp_when_config_is_valid(monkeypatch):
    """Valida envío SMTP con mock sin depender de servidor real."""

    settings = _build_smtp_settings()
    monkeypatch.setattr(email_service, "get_settings", lambda: settings)

    smtp_calls: dict[str, object] = {}

    class FakeSMTP:
        """Mock simple de cliente SMTP para pruebas."""

        def __init__(self, host, port, timeout):
            smtp_calls["host"] = host
            smtp_calls["port"] = port
            smtp_calls["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def ehlo(self):
            smtp_calls["ehlo"] = True

        def starttls(self, context=None):
            smtp_calls["starttls"] = True

        def login(self, user, password):
            smtp_calls["login"] = (user, password)

        def send_message(self, message):
            smtp_calls["subject"] = message["Subject"]
            smtp_calls["from"] = message["From"]
            smtp_calls["to"] = message["To"]

        def quit(self):
            smtp_calls["quit"] = True

    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

    result = email_service.send_alert_email(
        subject="Alerta crítica ManttoAI",
        message="Temperatura fuera de rango",
    )

    assert result.sent is True
    assert smtp_calls["host"] == "smtp.example.com"
    assert smtp_calls["port"] == 587
    assert smtp_calls["starttls"] is True
    assert smtp_calls["login"] == ("bot@example.com", "super-secret")
    assert smtp_calls["to"] == "alertas@example.com"


def test_send_alert_email_returns_not_sent_when_config_is_incomplete(monkeypatch):
    """Valida que sin configuración SMTP no se intente enviar correo."""

    settings = _build_smtp_settings(smtp_host="", smtp_to_email="")
    monkeypatch.setattr(email_service, "get_settings", lambda: settings)

    result = email_service.send_alert_email(
        subject="Alerta crítica ManttoAI",
        message="Vibración fuera de rango",
    )

    assert result.sent is False
    assert result.error is not None


def test_send_alert_email_returns_not_sent_when_smtp_client_fails(monkeypatch):
    """Valida que un error SMTP quede registrado sin romper el flujo."""

    import smtplib

    settings = _build_smtp_settings()
    monkeypatch.setattr(email_service, "get_settings", lambda: settings)

    class BrokenSMTP:
        """Mock SMTP que falla al iniciar TLS."""

        def __init__(self, _host, _port, timeout=None):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def ehlo(self):
            pass

        def starttls(self, context=None):
            raise smtplib.SMTPException("smtp unavailable")

        def quit(self):
            pass

    monkeypatch.setattr(email_service.smtplib, "SMTP", BrokenSMTP)

    result = email_service.send_alert_email(
        subject="Alerta crítica ManttoAI",
        message="Temperatura fuera de rango",
    )

    assert result.sent is False
    assert "Error SMTP: SMTPException" in str(result.error)
