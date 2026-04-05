"""Tests del servicio de email."""

from app.services.email_service import send_alert_email


def test_send_alert_email_returns_expected_shape():
    """Valida la respuesta del servicio de correo demo."""

    result = send_alert_email("Alerta", "Equipo fuera de umbral")
    assert set(result.keys()) == {"sent", "subject", "message"}
