"""Servicios de envío de correo."""

from app.config import get_settings


def can_send_email() -> bool:
    """Indica si la configuración SMTP mínima está presente."""

    settings = get_settings()
    return bool(settings.smtp_host and settings.smtp_user and settings.smtp_password)


def send_alert_email(subject: str, message: str) -> dict[str, str | bool]:
    """Simula el envío de un correo para el scaffold."""

    return {"sent": can_send_email(), "subject": subject, "message": message}
