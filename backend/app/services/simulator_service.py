"""Servicio de simulación de sensores IoT para demo.

Genera lecturas MQTT automáticas sin necesidad de hardware ESP32.
Diseñado para ser liviano y no sobrecargar el servidor.
"""

from __future__ import annotations

import json
import logging
import random
import threading
from collections.abc import Callable
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import get_settings

try:
    import paho.mqtt.client as mqtt
except ImportError:  # pragma: no cover
    mqtt = None

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except ImportError:  # pragma: no cover
    BackgroundScheduler = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)

SessionFactory = Callable[[], Session]

_simulator_scheduler = None
_simulator_lock = threading.Lock()
_SIMULATOR_JOB_ID = "simulador_iot"

# Perfiles de comportamiento por tipo de equipo para datos realistas
_EQUIPMENT_PROFILES: dict[str, dict[str, tuple[float, float]]] = {
    "compresor": {
        "temp_range": (40.0, 65.0),
        "humidity_range": (50.0, 75.0),
        "vib_base": (0.3, 0.7),
    },
    "bomba": {
        "temp_range": (35.0, 50.0),
        "humidity_range": (45.0, 65.0),
        "vib_base": (0.2, 0.5),
    },
    "motor": {
        "temp_range": (38.0, 58.0),
        "humidity_range": (48.0, 70.0),
        "vib_base": (0.25, 0.6),
    },
    "default": {
        "temp_range": (35.0, 55.0),
        "humidity_range": (45.0, 70.0),
        "vib_base": (0.2, 0.6),
    },
}


def _get_equipment_profile(tipo: str | None) -> dict[str, tuple[float, float]]:
    """Obtiene perfil de generación según tipo de equipo."""
    if not tipo:
        return _EQUIPMENT_PROFILES["default"]
    tipo_lower = tipo.strip().lower()
    return _EQUIPMENT_PROFILES.get(tipo_lower, _EQUIPMENT_PROFILES["default"])


def _build_reading(rng: random.Random, profile: dict[str, tuple[float, float]]) -> dict:
    """Genera una lectura simulada basada en el perfil del equipo."""
    temp_min, temp_max = profile["temp_range"]
    hum_min, hum_max = profile["humidity_range"]
    vib_min, vib_max = profile["vib_base"]

    return {
        "temperatura": round(rng.uniform(temp_min, temp_max), 2),
        "humedad": round(rng.uniform(hum_min, hum_max), 2),
        "vib_x": round(rng.uniform(vib_min, vib_max), 3),
        "vib_y": round(rng.uniform(vib_min * 0.5, vib_max * 0.8), 3),
        "vib_z": round(rng.uniform(9.5, 10.1), 3),  # Gravedad + ruido
        "timestamp": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
    }


def _resolve_session_factory(session_factory: SessionFactory | None) -> SessionFactory:
    """Resuelve SessionFactory con fallback lazy."""
    if session_factory is not None:
        return session_factory
    from app.database import SessionLocal

    return SessionLocal


def run_simulator_cycle(session_factory: SessionFactory | None = None) -> dict:
    """Ejecuta un ciclo de simulación publicando lecturas para equipos activos.

    Retorna un resumen de la ejecución.
    """
    settings = get_settings()
    resolved_factory = _resolve_session_factory(session_factory)

    if mqtt is None:
        logger.warning("paho-mqtt no disponible, simulador omitido")
        return {"status": "skipped", "reason": "mqtt_unavailable"}

    # Obtener equipos activos de la BD
    session = resolved_factory()
    equipos_data: list[tuple[int, str | None]] = []

    try:
        from app.services.equipo_service import list_equipos

        for equipo in list_equipos(session):
            estado = getattr(equipo, "estado", "").strip().lower()
            if estado in {"operativo", "activo"}:
                equipos_data.append((equipo.id, getattr(equipo, "tipo", None)))
    finally:
        session.close()

    if not equipos_data:
        logger.debug("Simulador: no hay equipos activos")
        return {"status": "ok", "equipos": 0, "publicados": 0}

    # Conectar MQTT
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if settings.mqtt_username:
            client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
        client.connect(settings.mqtt_broker_host, settings.mqtt_broker_port)
    except Exception as exc:
        logger.warning("Simulador: error conectando MQTT: %s", exc)
        return {"status": "error", "reason": str(exc)}

    # Publicar lecturas
    rng = random.Random()  # Sin seed para variación real
    publicados = 0

    try:
        for equipo_id, tipo in equipos_data:
            profile = _get_equipment_profile(tipo)
            reading = _build_reading(rng, profile)
            topic = f"{settings.mqtt_base_topic}/{equipo_id}/lecturas"

            result = client.publish(topic, json.dumps(reading))
            if result.rc == 0:
                publicados += 1
                logger.debug("Simulador: publicado en %s", topic)
            else:
                logger.warning(
                    "Simulador: fallo publicando en %s rc=%d", topic, result.rc
                )
    finally:
        client.disconnect()

    logger.info(
        "Simulador: ciclo completado equipos=%d publicados=%d",
        len(equipos_data),
        publicados,
    )

    return {
        "status": "ok",
        "equipos": len(equipos_data),
        "publicados": publicados,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def is_simulator_running() -> bool:
    """Indica si el simulador está activo."""
    with _simulator_lock:
        scheduler = _simulator_scheduler

    if scheduler is None:
        return False

    running = getattr(scheduler, "running", None)
    if isinstance(running, bool):
        return running

    started = getattr(scheduler, "started", None)
    return bool(started) if isinstance(started, bool) else False


def start_simulator(session_factory: SessionFactory | None = None) -> bool:
    """Inicia el simulador de sensores IoT según configuración."""
    global _simulator_scheduler

    settings = get_settings()

    if not settings.simulator_enabled:
        logger.info("Simulador IoT deshabilitado por configuración")
        return False

    if not settings.mqtt_enabled:
        logger.info("Simulador IoT requiere MQTT habilitado")
        return False

    if settings.simulator_interval_seconds <= 0:
        logger.warning(
            "Intervalo inválido para simulador: %s", settings.simulator_interval_seconds
        )
        return False

    if BackgroundScheduler is None:
        logger.warning("APScheduler no disponible para simulador")
        return False

    resolved_factory = _resolve_session_factory(session_factory)
    if not callable(resolved_factory):
        logger.error("SessionFactory inválido para simulador")
        return False

    with _simulator_lock:
        if _simulator_scheduler is not None:
            return True

        scheduler = BackgroundScheduler(timezone="UTC")
        try:
            scheduler.add_job(
                run_simulator_cycle,
                "interval",
                id=_SIMULATOR_JOB_ID,
                seconds=settings.simulator_interval_seconds,
                max_instances=1,
                coalesce=True,
                replace_existing=True,
                kwargs={"session_factory": resolved_factory},
            )
            scheduler.start()
        except Exception:
            logger.exception("No se pudo iniciar el simulador")
            try:
                scheduler.shutdown(wait=False)
            except Exception:
                pass
            return False

        _simulator_scheduler = scheduler

    logger.info(
        "Simulador IoT iniciado job_id=%s (intervalo=%s segundos)",
        _SIMULATOR_JOB_ID,
        settings.simulator_interval_seconds,
    )
    return True


def stop_simulator() -> None:
    """Detiene el simulador si está activo."""
    global _simulator_scheduler

    with _simulator_lock:
        if _simulator_scheduler is None:
            return

        try:
            _simulator_scheduler.shutdown(wait=False)
        finally:
            _simulator_scheduler = None

    logger.info("Simulador IoT detenido")
