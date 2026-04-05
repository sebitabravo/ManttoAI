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
) -> SimpleNamespace:
    """Construye settings SMTP para pruebas unitarias."""

    return SimpleNamespace(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        smtp_from_email=smtp_from_email,
        smtp_to_email=smtp_to_email,
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

        def starttls(self):
            smtp_calls["starttls"] = True

        def login(self, user, password):
            smtp_calls["login"] = (user, password)

        def send_message(self, message):
            smtp_calls["subject"] = message["Subject"]
            smtp_calls["from"] = message["From"]
            smtp_calls["to"] = message["To"]

    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

    result = email_service.send_alert_email(
        subject="Alerta crítica ManttoAI",
        message="Temperatura fuera de rango",
    )

    assert result["sent"] is True
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

    assert result["sent"] is False
    assert "error" in result


def test_send_alert_email_returns_not_sent_when_smtp_client_fails(monkeypatch):
    """Valida que un error SMTP quede registrado sin romper el flujo."""

    settings = _build_smtp_settings()
    monkeypatch.setattr(email_service, "get_settings", lambda: settings)

    class BrokenSMTP:
        """Mock SMTP que falla al iniciar TLS."""

        def __init__(self, _host, _port, _timeout):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self):
            raise RuntimeError("smtp unavailable")

    monkeypatch.setattr(email_service.smtplib, "SMTP", BrokenSMTP)

    result = email_service.send_alert_email(
        subject="Alerta crítica ManttoAI",
        message="Temperatura fuera de rango",
    )

    assert result["sent"] is False
    assert "smtp unavailable" in str(result.get("error"))
