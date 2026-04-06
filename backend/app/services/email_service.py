"""Servicios de envío de correo."""

import logging
import smtplib
import ssl
import time
from contextlib import contextmanager
from email.message import EmailMessage
from smtplib import SMTPAuthenticationError, SMTPException
from typing import Generator

from app.config import get_settings
from app.schemas.email import EmailResponse

logger = logging.getLogger(__name__)


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


def _sanitize_smtp_error(exc: Exception) -> str:
    """Sanitiza mensajes de error SMTP para evitar exposición de información sensible."""

    if isinstance(exc, SMTPAuthenticationError):
        return "Error de autenticación SMTP"
    if isinstance(exc, SMTPException):
        # Solo incluir el tipo de error, no detalles internos
        return f"Error SMTP: {exc.__class__.__name__}"
    return "Error al enviar email"


@contextmanager
def get_smtp_client() -> Generator[smtplib.SMTP | smtplib.SMTP_SSL, None, None]:
    """
    Context manager para obtener un cliente SMTP autenticado.

    Soporta tanto SMTP con STARTTLS (puerto 587) como SMTP_SSL implícito (puerto 465).
    """

    settings = get_settings()
    if not can_send_email():
        raise RuntimeError("Configuración SMTP incompleta")

    timeout = settings.smtp_timeout
    use_ssl = settings.smtp_use_ssl

    if use_ssl:
        # SMTP con SSL implícito (típicamente puerto 465)
        context = ssl.create_default_context()
        client = smtplib.SMTP_SSL(
            settings.smtp_host, settings.smtp_port, timeout=timeout, context=context
        )
        try:
            client.login(settings.smtp_user, settings.smtp_password)
            yield client
        finally:
            try:
                client.quit()
            except Exception:
                pass
    else:
        # SMTP con STARTTLS (típicamente puerto 587)
        client = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=timeout)
        try:
            client.ehlo()
            client.starttls(context=ssl.create_default_context())
            client.ehlo()
            client.login(settings.smtp_user, settings.smtp_password)
            yield client
        finally:
            try:
                client.quit()
            except Exception:
                pass


def send_alert_email_with_client(
    smtp_client: smtplib.SMTP | smtplib.SMTP_SSL, subject: str, message: str
) -> EmailResponse:
    """
    Envía un correo de alerta reutilizando un cliente SMTP existente.

    Implementa retry con backoff exponencial para errores transitorios.
    """

    settings = get_settings()
    sender = settings.smtp_from_email or settings.smtp_user
    recipient = settings.smtp_to_email or settings.smtp_user

    email_message = EmailMessage()
    email_message["Subject"] = subject
    email_message["From"] = sender
    email_message["To"] = recipient
    email_message.set_content(message)

    max_attempts = settings.smtp_retry_attempts
    backoff_base = settings.smtp_retry_backoff
    last_exc = None

    for attempt in range(1, max_attempts + 1):
        try:
            smtp_client.send_message(email_message)
            if attempt > 1:
                logger.info(
                    "Email enviado exitosamente después de %d intentos", attempt
                )
            return EmailResponse(sent=True, subject=subject, message=message)
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "Intento %d/%d de envío SMTP falló: %s",
                attempt,
                max_attempts,
                _sanitize_smtp_error(exc),
            )
            if attempt < max_attempts:
                sleep_time = backoff_base * (2 ** (attempt - 1))
                logger.debug("Reintentando en %.2f segundos...", sleep_time)
                time.sleep(sleep_time)
            else:
                logger.error(
                    "Email no enviado después de %d intentos: %s",
                    max_attempts,
                    _sanitize_smtp_error(last_exc),
                )
                return EmailResponse(
                    sent=False,
                    subject=subject,
                    message=message,
                    error=_sanitize_smtp_error(last_exc),
                )

    # Fallback (no debería alcanzarse)
    return EmailResponse(
        sent=False,
        subject=subject,
        message=message,
        error="Error desconocido en retry loop",
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
        sanitized_error = _sanitize_smtp_error(exc)
        logger.exception("Error al conectar con servidor SMTP: %s", sanitized_error)
        return EmailResponse(
            sent=False, subject=subject, message=message, error=sanitized_error
        )
