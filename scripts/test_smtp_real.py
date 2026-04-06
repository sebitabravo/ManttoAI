"""Script para validar envío real de email SMTP."""

import os
import sys
from pathlib import Path

# Agregar backend al path
backend_path = Path(__file__).resolve().parents[1] / "backend"
sys.path.append(str(backend_path))

from app.services.email_service import send_alert_email, can_send_email
from app.config import get_settings


def test_real_smtp():
    """Prueba el envío real de email usando la configuración de .env."""

    settings = get_settings()

    print("--- Validación de Configuración SMTP ---")
    print(f"Host: {settings.smtp_host}")
    print(f"Port: {settings.smtp_port}")
    # No imprimimos el usuario por seguridad
    print(f"From: {settings.smtp_from_email or settings.smtp_user}")
    print(f"To: {settings.smtp_to_email or settings.smtp_user}")

    if not can_send_email():
        print("\nERROR: Configuración SMTP incompleta en .env")
        print("Asegúrate de configurar SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD")
        return

    print("\nEnviando email de prueba...")
    result = send_alert_email(
        subject="[TEST] Alerta Crítica Real - ManttoAI",
        message="Esta es una prueba de integración con SMTP real para validar el canal de notificaciones.",
    )

    if result["sent"]:
        print("\nSUCCESS: Email enviado correctamente.")
    else:
        print(f"\nFAILED: No se pudo enviar el email. Error: {result.get('error')}")


if __name__ == "__main__":
    test_real_smtp()
