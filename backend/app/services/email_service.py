"""Servicios de envío de correo."""

import smtplib
from email.message import EmailMessage

from app.config import get_settings


def can_send_email() -> bool:
    """Indica si la configuración SMTP mínima está presente."""

    settings = get_settings()
    sender = settings.smtp_from_email or settings.smtp_user
    recipient = settings.smtp_to_email or settings.smtp_user
    return bool(
        settings.smtp_host
        and settings.smtp_port is not None
        and settings.smtp_user
        and settings.smtp_password
        and sender
        and recipient
    )


def send_alert_email(subject: str, message: str) -> dict[str, str | bool | None]:
    """Intenta enviar un correo de alerta usando SMTP configurado."""

    response: dict[str, str | bool | None] = {
        "sent": False,
        "subject": subject,
        "message": message,
        "error": None,
    }

    if not can_send_email():
        response["error"] = "Configuración SMTP incompleta"
        return response

    settings = get_settings()
    sender = settings.smtp_from_email or settings.smtp_user
    recipient = settings.smtp_to_email or settings.smtp_user

    email_message = EmailMessage()
    email_message["Subject"] = subject
    email_message["From"] = sender
    email_message["To"] = recipient
    email_message.set_content(message)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, 10) as smtp_client:
            smtp_client.starttls()
            smtp_client.login(settings.smtp_user, settings.smtp_password)
            smtp_client.send_message(email_message)
    except Exception as exc:
        response["error"] = str(exc)
        return response

    response["sent"] = True
    return response
