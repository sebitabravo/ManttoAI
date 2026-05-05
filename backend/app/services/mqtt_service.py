"""Servicios de ingesta MQTT para lecturas telemétricas."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from socket import gaierror

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.schemas.lectura import LecturaMqttPayload
from app.models.equipo import Equipo
from app.services.lectura_service import create_lectura_from_mqtt_payload

# Configuración de reintentos para tolerancia a fallos de DB (RNF-17)
_MQTT_DB_RETRY_ATTEMPTS = 3
_MQTT_DB_RETRY_BACKOFF_SECONDS = 1.0

try:
    import paho.mqtt.client as mqtt
except ImportError:  # pragma: no cover - fallback defensivo
    mqtt = None

logger = logging.getLogger(__name__)

SessionFactory = Callable[[], Session]

_mqtt_client = None


def _normalize_base_topic(raw: str) -> str:
    """Normaliza mqtt_base_topic eliminando slashes al inicio y al final."""

    return raw.strip("/")


def build_topic(mac_address: str) -> str:
    """Construye el topic MQTT esperado para un equipo."""

    settings = get_settings()
    base = _normalize_base_topic(settings.mqtt_telemetry_topic)
    return f"{base}/{mac_address}"


def build_subscription_topic() -> str:
    """Construye el topic de suscripción wildcard para todas las lecturas."""

    settings = get_settings()
    base = _normalize_base_topic(settings.mqtt_telemetry_topic)
    return f"{base}/+"


def extract_mac_address(topic: str) -> str:
    """Extrae mac_address desde un topic `manttoai/telemetria/{mac_address}`."""

    settings = get_settings()
    # Usar la misma normalización que build_topic para consistencia
    base_parts = _normalize_base_topic(settings.mqtt_telemetry_topic).split("/")
    topic_parts = topic.strip("/").split("/")

    expected_len = len(base_parts) + 1
    if len(topic_parts) != expected_len:
        raise ValueError("Topic MQTT inválido")

    if topic_parts[: len(base_parts)] != base_parts:
        raise ValueError("Topic MQTT inválido")

    return topic_parts[-1]


MAX_PAYLOAD_BYTES = 4096  # Límite para prevenir DoS por payloads enormes


def parse_message(payload: str | bytes) -> LecturaMqttPayload:
    """Parsea y valida un payload MQTT para lecturas."""

    if isinstance(payload, bytes):
        if len(payload) > MAX_PAYLOAD_BYTES:
            raise ValueError("Payload MQTT excede tamaño máximo")
        try:
            payload_text = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Payload MQTT no está codificado en UTF-8") from exc
    else:
        if len(payload) > MAX_PAYLOAD_BYTES:
            raise ValueError("Payload MQTT excede tamaño máximo")
        payload_text = payload

    try:
        payload_data = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise ValueError("Payload MQTT no es JSON válido") from exc

    try:
        return LecturaMqttPayload.model_validate(payload_data)
    except ValidationError as exc:
        raise ValueError("Payload MQTT inválido") from exc


def _persist_lectura_with_retry(
    topic: str,
    mac_address: str,
    lectura_payload: LecturaMqttPayload,
    session_factory: SessionFactory,
    max_attempts: int = _MQTT_DB_RETRY_ATTEMPTS,
    backoff_seconds: float = _MQTT_DB_RETRY_BACKOFF_SECONDS,
) -> bool:
    """
    Persiste una lectura MQTT con reintentos automáticos ante fallos de DB.

    Implementa tolerancia a fallos operacionales (RNF-17): si la DB cae
    momentáneamente durante la operación, reintenta hasta max_attempts veces
    con backoff exponencial antes de descartar el mensaje.

    Solo reintenta ante OperationalError (DB no disponible). Errores de
    validación o negocio (HTTPException) se descartan inmediatamente.
    """
    for intento in range(1, max_attempts + 1):
        db = session_factory()
        try:
            equipo = db.query(Equipo).filter(Equipo.mac_address == mac_address).first()
            if not equipo:
                logger.warning(
                    "[MQTT] Equipo no encontrado para mac_address=%s", mac_address
                )
                return False

            lectura = create_lectura_from_mqtt_payload(
                db, equipo.id, lectura_payload, background_tasks=None
            )
            logger.info(
                "[MQTT] Lectura persistida: equipo_id=%d lectura_id=%s "
                "timestamp=%s temp=%.1f humedad=%.1f",
                equipo.id,
                getattr(lectura, "id", "n/a"),
                getattr(lectura, "timestamp", "n/a"),
                lectura_payload.temperatura or 0,
                lectura_payload.humedad or 0,
            )
            return True
        except HTTPException as exc:
            # Error de negocio (equipo no existe, etc.) — no reintentar
            logger.warning(
                "No se persistió lectura MQTT topic=%s detalle=%s",
                topic,
                exc.detail,
            )
            return False
        except OperationalError as exc:
            # DB no disponible momentáneamente — reintentar con backoff
            if intento < max_attempts:
                espera = backoff_seconds * intento
                logger.warning(
                    "[MQTT] DB no disponible (intento %d/%d) topic=%s error=%s — "
                    "reintentando en %.1fs",
                    intento,
                    max_attempts,
                    topic,
                    str(exc),
                    espera,
                )
                time.sleep(espera)
            else:
                logger.error(
                    "[MQTT] DB no disponible tras %d intentos topic=%s — "
                    "lectura descartada",
                    max_attempts,
                    topic,
                )
                return False
        except (SQLAlchemyError, RuntimeError, OSError):
            logger.exception("Error inesperado procesando mensaje MQTT topic=%s", topic)
            return False
        finally:
            db.close()

    return False  # pragma: no cover — alcanzado solo si max_attempts == 0


def process_mqtt_message(
    topic: str,
    payload: str | bytes,
    session_factory: SessionFactory = SessionLocal,
) -> bool:
    """Procesa un mensaje MQTT y persiste lectura sin romper el loop."""

    try:
        mac_address = extract_mac_address(topic)
        lectura_payload = parse_message(payload)
    except ValueError as exc:
        logger.warning("Mensaje MQTT descartado topic=%s error=%s", topic, str(exc))
        return False

    return _persist_lectura_with_retry(
        topic=topic,
        mac_address=mac_address,
        lectura_payload=lectura_payload,
        session_factory=session_factory,
    )


def _on_connect(client, _userdata, _flags, reason_code, _properties) -> None:
    """Callback de conexión MQTT para suscribirse al topic de lecturas."""

    if reason_code != 0:
        logger.warning("Conexión MQTT rechazada: reason_code=%s", reason_code)
        return

    topic = build_subscription_topic()
    result, _mid = client.subscribe(topic)
    if mqtt is not None and result != mqtt.MQTT_ERR_SUCCESS:
        logger.warning("No se pudo suscribir a topic MQTT: %s", topic)
        return

    logger.info("Suscripción MQTT activa en topic: %s", topic)


def _on_message(_client, userdata, msg) -> None:
    """Callback de mensaje MQTT que delega en el procesador de lectura."""

    session_factory = SessionLocal
    if isinstance(userdata, dict) and "session_factory" in userdata:
        session_factory = userdata["session_factory"]

    process_mqtt_message(msg.topic, msg.payload, session_factory=session_factory)


def start_mqtt_subscriber(session_factory: SessionFactory = SessionLocal) -> bool:
    """Inicia subscriber MQTT sin bloquear el arranque del backend."""

    global _mqtt_client

    if mqtt is None:
        logger.warning("paho-mqtt no está disponible; se omite subscriber MQTT")
        return False

    if _mqtt_client is not None:
        return True

    settings = get_settings()
    callback_api_version = None
    callback_api_enum = getattr(mqtt, "CallbackAPIVersion", None)
    if callback_api_enum is not None:
        callback_api_version = getattr(callback_api_enum, "VERSION2", None)

    if callback_api_version is not None:
        client = mqtt.Client(callback_api_version)
    else:
        client = mqtt.Client()

    mqtt_username = settings.mqtt_username.strip()
    if mqtt_username:
        client.username_pw_set(mqtt_username, settings.mqtt_password)

    client.user_data_set({"session_factory": session_factory})
    client.on_connect = _on_connect
    client.on_message = _on_message

    try:
        client.connect(settings.mqtt_broker_host, settings.mqtt_broker_port)
        client.loop_start()
    except (OSError, ValueError, gaierror) as exc:
        logger.warning(
            "No se pudo iniciar subscriber MQTT en %s:%s (%s: %s)",
            settings.mqtt_broker_host,
            settings.mqtt_broker_port,
            type(exc).__name__,
            str(exc),
        )
        return False

    _mqtt_client = client
    logger.info(
        "Subscriber MQTT iniciado en %s:%s",
        settings.mqtt_broker_host,
        settings.mqtt_broker_port,
    )
    return True


def stop_mqtt_subscriber() -> None:
    """Detiene el subscriber MQTT si está activo."""

    global _mqtt_client

    if _mqtt_client is None:
        return

    try:
        _mqtt_client.loop_stop()
        _mqtt_client.disconnect()
    finally:
        _mqtt_client = None
