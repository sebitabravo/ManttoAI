"""Tests de integración para validación de SMTP real."""

import pytest
from app.services.email_service import send_alert_email, can_send_email
from app.config import get_settings


@pytest.mark.integration
def test_real_smtp_integration():
    """
    Prueba el envío real de email usando la configuración de .env.
    Este test solo se ejecuta si se especifica explícitamente y hay configuración.
    """

    if not can_send_email():
        pytest.skip("Configuración SMTP incompleta en .env para test de integración")

    settings = get_settings()
    print(f"\nProbando SMTP real en {settings.smtp_host}:{settings.smtp_port}")

    result = send_alert_email(
        subject="[INTEGRATION TEST] Alerta Crítica Real - ManttoAI",
        message="Esta es una prueba de integración automatizada con SMTP real.",
    )

    assert result.sent is True, f"Falla en envío SMTP: {result.error}"
    assert result.error is None
