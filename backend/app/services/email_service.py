"""Servicios de envío de correo."""

import smtplib
from contextlib import contextmanager
from email.message import EmailMessage
from typing import Generator

from app.config import get_settings
from app.schemas.email import EmailResponse


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


@contextmanager
def get_smtp_client() -> Generator[smtplib.SMTP, None, None]:
    """Context manager para obtener un cliente SMTP autenticado."""

    settings = get_settings()
    if not can_send_email():
        raise RuntimeError("Configuración SMTP incompleta")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, 10) as smtp_client:
        smtp_client.starttls()
        smtp_client.login(settings.smtp_user, settings.smtp_password)
        yield smtp_client


def send_alert_email_with_client(
    smtp_client: smtplib.SMTP, subject: str, message: str
) -> EmailResponse:
    """Envía un correo de alerta reutilizando un cliente SMTP existente."""

    settings = get_settings()
    sender = settings.smtp_from_email or settings.smtp_user
    recipient = settings.smtp_to_email or settings.smtp_user

    email_message = EmailMessage()
    email_message["Subject"] = subject
    email_message["From"] = sender
    email_message["To"] = recipient
    email_message.set_content(message)

    try:
        smtp_client.send_message(email_message)
        return EmailResponse(sent=True, subject=subject, message=message)
    except Exception as exc:
        return EmailResponse(
            sent=False, subject=subject, message=message, error=str(exc)
        )


def send_alert_email(subject: str, message: str) -> EmailResponse:
    """Intenta enviar un correo de alerta usando SMTP configurado."""

    if not can_send_email():
        return EmailResponse(
            sent=False,
            subject=subject,
            message=message,
            error="Configuración SMTP incompleta",
        )

    try:
        with get_smtp_client() as smtp_client:
            return send_alert_email_with_client(smtp_client, subject, message)
    except Exception as exc:
        return EmailResponse(
            sent=False, subject=subject, message=message, error=str(exc)
        )
