"""Servicio de notificaciones via Twilio (WhatsApp y SMS)."""

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from app.config import get_settings
from app.schemas.notification import NotificationResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Pool reutilizable para tareas IO-bound sin bloquear el event loop
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="twilio")


def _enmascarar_numero(numero: str) -> str:
    """Enmascara un numero mostrando solo los ultimos 4 digitos."""
    limpio = numero.replace("+", "").replace(" ", "")
    if len(limpio) <= 4:
        return f"****{limpio[-4:]}"
    return f"+{limpio[:2]}****{limpio[-4:]}"


def _tiene_credenciales() -> bool:
    """Verifica si las credenciales Twilio minimas estan configuradas."""
    settings = get_settings()
    return bool(
        settings.twilio_account_sid
        and settings.twilio_auth_token
        and settings.twilio_phone_number
    )


def _get_twilio_client():
    """Crea y retorna un cliente Twilio autenticado."""
    from twilio.rest import Client

    settings = get_settings()
    return Client(settings.twilio_account_sid, settings.twilio_auth_token)


def _ejecutar_envio_whatsapp(to_number: str, message: str) -> NotificationResponse:
    """Ejecuta el envio de un mensaje WhatsApp via Twilio (bloqueante, correr en thread)."""
    if not _tiene_credenciales():
        return NotificationResponse(
            sent=False,
            channel="whatsapp",
            message=message,
            to_number=_enmascarar_numero(to_number),
            error="Configuracion Twilio incompleta",
        )

    settings = get_settings()
    twilio_from = f"whatsapp:{settings.twilio_phone_number}"
    twilio_to = f"whatsapp:{to_number}"

    try:
        logger.info(
            "[TWILIO-WA] Enviando WhatsApp a %s", _enmascarar_numero(to_number)
        )
        client = _get_twilio_client()
        twilio_msg = client.messages.create(
            body=message,
            from_=twilio_from,
            to=twilio_to,
        )
        logger.info(
            "[TWILIO-WA] Enviado exitosamente: sid=%s to=%s",
            twilio_msg.sid,
            _enmascarar_numero(to_number),
        )
        return NotificationResponse(
            sent=True,
            channel="whatsapp",
            message=message,
            to_number=_enmascarar_numero(to_number),
            sid=twilio_msg.sid,
        )
    except Exception as exc:
        logger.error(
            "[TWILIO-WA] Error al enviar WhatsApp a %s: %s: %s",
            _enmascarar_numero(to_number),
            exc.__class__.__name__,
            exc,
        )
        return NotificationResponse(
            sent=False,
            channel="whatsapp",
            message=message,
            to_number=_enmascarar_numero(to_number),
            error=_sanitizar_error_twilio(exc),
        )


def _ejecutar_envio_sms(to_number: str, message: str) -> NotificationResponse:
    """Ejecuta el envio de un SMS via Twilio (bloqueante, correr en thread)."""
    if not _tiene_credenciales():
        return NotificationResponse(
            sent=False,
            channel="sms",
            message=message,
            to_number=_enmascarar_numero(to_number),
            error="Configuracion Twilio incompleta",
        )

    settings = get_settings()

    try:
        logger.info("[TWILIO-SMS] Enviando SMS a %s", _enmascarar_numero(to_number))
        client = _get_twilio_client()
        twilio_msg = client.messages.create(
            body=message,
            from_=settings.twilio_phone_number,
            to=to_number,
        )
        logger.info(
            "[TWILIO-SMS] Enviado exitosamente: sid=%s to=%s",
            twilio_msg.sid,
            _enmascarar_numero(to_number),
        )
        return NotificationResponse(
            sent=True,
            channel="sms",
            message=message,
            to_number=_enmascarar_numero(to_number),
            sid=twilio_msg.sid,
        )
    except Exception as exc:
        logger.error(
            "[TWILIO-SMS] Error al enviar SMS a %s: %s: %s",
            _enmascarar_numero(to_number),
            exc.__class__.__name__,
            exc,
        )
        return NotificationResponse(
            sent=False,
            channel="sms",
            message=message,
            to_number=_enmascarar_numero(to_number),
            error=_sanitizar_error_twilio(exc),
        )


def _sanitizar_error_twilio(exc: Exception) -> str:
    """Sanitiza mensajes de error Twilio para no exponer datos sensibles."""
    exc_name = exc.__class__.__name__
    # Errores conocidos de twilio.rest
    if exc_name == "TwilioRestException":
        return f"Error Twilio API: {getattr(exc, 'code', 'desconocido')}"
    if exc_name in ("AuthenticationError", "RequestError"):
        return f"Error de conexion con Twilio: {exc_name}"
    return "Error al enviar notificacion Twilio"


class NotificationService:
    """Servicio de notificaciones via Twilio (WhatsApp y SMS).

    Todos los metodos que interactuan con la API de Twilio ejecutan la
    llamada en un ThreadPoolExecutor para no bloquear el event loop.
    """

    def __init__(self) -> None:
        self._credenciales_presentes = _tiene_credenciales()
        if not self._credenciales_presentes:
            logger.warning(
                "[TWILIO] Credenciales Twilio no configuradas. "
                "Las notificaciones WhatsApp/SMS estaran deshabilitadas."
            )

    # ------------------------------------------------------------------
    # Metodos publicos (retornan awaitables o dicts)
    # ------------------------------------------------------------------

    def send_whatsapp(self, to_number: str, message: str) -> dict:
        """Envia un mensaje WhatsApp via Twilio.

        La llamada a la API de Twilio se ejecuta en un thread separado.
        Retorna un dict con la misma estructura que NotificationResponse.
        """
        if not self._credenciales_presentes:
            return self._respuesta_error(
                "whatsapp", to_number, message, "Configuracion Twilio incompleta"
            )

        future = _executor.submit(_ejecutar_envio_whatsapp, to_number, message)
        resultado = future.result()
        return resultado.model_dump()

    def send_sms(self, to_number: str, message: str) -> dict:
        """Envia un SMS via Twilio.

        La llamada a la API de Twilio se ejecuta en un thread separado.
        Retorna un dict con la misma estructura que NotificationResponse.
        """
        if not self._credenciales_presentes:
            return self._respuesta_error(
                "sms", to_number, message, "Configuracion Twilio incompleta"
            )

        future = _executor.submit(_ejecutar_envio_sms, to_number, message)
        resultado = future.result()
        return resultado.model_dump()

    def send_critical_alert(
        self, user, message: str, db: "Session"
    ) -> dict:
        """Envia una alerta critica: intenta WhatsApp primero, SMS como fallback.

        Estrategia:
          1. Intenta WhatsApp
          2. Si falla, envia SMS
          3. Registra el resultado en AuditLog con entity_type='notificacion'

        Si el usuario no tiene telefono registrado, retorna error sin intentar envio.
        Si no hay credenciales Twilio configuradas, retorna error elegante (no
        lanza excepcion).
        """
        from app.services.audit_service import log_audit

        if not self._credenciales_presentes:
            logger.warning(
                "[TWILIO] Intento de alerta critica sin credenciales configuradas"
            )
            log_audit(
                db=db,
                action="send_critical_alert",
                entity_type="notificacion",
                entity_id=getattr(user, "id", None),
                usuario_id=getattr(user, "id", None),
                new_values={
                    "error": "Credenciales Twilio no configuradas",
                    "canal": "ninguno",
                },
            )
            return self._respuesta_error(
                "whatsapp",
                getattr(user, "telefono", ""),
                message,
                "Twilio no configurado",
            )

        telefono = getattr(user, "telefono", None)
        if not telefono:
            logger.warning(
                "[TWILIO] Usuario %s no tiene telefono registrado",
                getattr(user, "id", "desconocido"),
            )
            log_audit(
                db=db,
                action="send_critical_alert",
                entity_type="notificacion",
                entity_id=getattr(user, "id", None),
                usuario_id=getattr(user, "id", None),
                new_values={"error": "Usuario sin telefono", "canal": "ninguno"},
            )
            return self._respuesta_error(
                "whatsapp", "", message, "Usuario sin telefono registrado"
            )

        # --- Intento 1: WhatsApp ---
        logger.info(
            "[TWILIO] Alerta critica: intentando WhatsApp para usuario %s",
            getattr(user, "id", "desconocido"),
        )
        future_wa = _executor.submit(_ejecutar_envio_whatsapp, telefono, message)
        resultado_wa = future_wa.result()

        if resultado_wa.sent:
            log_audit(
                db=db,
                action="send_critical_alert",
                entity_type="notificacion",
                entity_id=getattr(user, "id", None),
                usuario_id=getattr(user, "id", None),
                new_values={
                    "canal": "whatsapp",
                    "sid": resultado_wa.sid,
                    "to": _enmascarar_numero(telefono),
                },
            )
            logger.info(
                "[TWILIO] Alerta critica enviada por WhatsApp a usuario %s: sid=%s",
                getattr(user, "id", "desconocido"),
                resultado_wa.sid,
            )
            return resultado_wa.model_dump()

        # --- Intento 2 (fallback): SMS ---
        logger.warning(
            "[TWILIO] WhatsApp fallo para usuario %s, intentando SMS como fallback. "
            "Error: %s",
            getattr(user, "id", "desconocido"),
            resultado_wa.error,
        )
        future_sms = _executor.submit(_ejecutar_envio_sms, telefono, message)
        resultado_sms = future_sms.result()

        if resultado_sms.sent:
            log_audit(
                db=db,
                action="send_critical_alert",
                entity_type="notificacion",
                entity_id=getattr(user, "id", None),
                usuario_id=getattr(user, "id", None),
                new_values={
                    "canal": "sms_fallback",
                    "sid": resultado_sms.sid,
                    "to": _enmascarar_numero(telefono),
                    "whatsapp_error": resultado_wa.error,
                },
            )
            logger.info(
                "[TWILIO] Alerta critica enviada por SMS (fallback) a usuario %s: sid=%s",
                getattr(user, "id", "desconocido"),
                resultado_sms.sid,
            )
            return resultado_sms.model_dump()

        # --- Ambos canales fallaron ---
        error_msg = (
            f"WhatsApp: {resultado_wa.error} | "
            f"SMS: {resultado_sms.error}"
        )
        logger.error(
            "[TWILIO] Alerta critica FALLIDA para usuario %s: %s",
            getattr(user, "id", "desconocido"),
            error_msg,
        )
        log_audit(
            db=db,
            action="send_critical_alert",
            entity_type="notificacion",
            entity_id=getattr(user, "id", None),
            usuario_id=getattr(user, "id", None),
            new_values={"error": error_msg, "canal": "ninguno"},
        )
        return NotificationResponse(
            sent=False,
            channel="whatsapp_sms_fallback",
            message=message,
            to_number=_enmascarar_numero(telefono),
            error=error_msg,
        ).model_dump()

    # ------------------------------------------------------------------
    # Metodos internos
    # ------------------------------------------------------------------

    def _respuesta_error(
        self, channel: str, to_number: str, message: str, error: str
    ) -> dict:
        """Retorna un dict de error consistente sin llamar a Twilio."""
        return NotificationResponse(
            sent=False,
            channel=channel,
            message=message,
            to_number=_enmascarar_numero(to_number) if to_number else "",
            error=error,
        ).model_dump()
