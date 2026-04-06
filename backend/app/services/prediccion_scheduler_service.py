"""Scheduler liviano para ejecutar predicciones periódicas."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import threading
from collections.abc import Callable
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.services.equipo_service import list_equipos
from app.services.prediccion_service import execute_prediction

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except ImportError:  # pragma: no cover - fallback defensivo
    BackgroundScheduler = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)

SessionFactory = Callable[[], Session]

_prediction_scheduler = None
_prediction_scheduler_lock = threading.Lock()
_PREDICTION_JOB_ID = "predicciones_periodicas"


def _is_equipo_activo(estado: str | None) -> bool:
    """Determina si un equipo debe participar en la ejecución periódica."""

    if not isinstance(estado, str):
        return False

    estado_normalizado = estado.strip().lower()
    return estado_normalizado in {"operativo", "activo"}


def _resolve_session_factory(session_factory: SessionFactory | None) -> SessionFactory:
    """Resuelve SessionFactory con fallback lazy para evitar side effects."""

    if session_factory is not None:
        return session_factory

    from app.database import SessionLocal

    return SessionLocal


def run_periodic_predictions(
    session_factory: SessionFactory | None = None,
) -> dict[str, int | str]:
    """Ejecuta inferencias para equipos activos sin detener el scheduler."""

    resolved_session_factory = _resolve_session_factory(session_factory)
    if not callable(resolved_session_factory):
        raise ValueError("session_factory debe ser invocable")

    listing_session = resolved_session_factory()
    if listing_session is None or not hasattr(listing_session, "close"):
        raise ValueError("session_factory debe retornar una sesión válida")

    active_equipo_ids: list[int] = []
    dialect_name = ""

    try:
        dialect_name = getattr(getattr(listing_session, "bind", None), "dialect", None)
        dialect_name = getattr(dialect_name, "name", "")

        for equipo in list_equipos(listing_session):
            if _is_equipo_activo(getattr(equipo, "estado", None)):
                active_equipo_ids.append(int(equipo.id))
    finally:
        if listing_session is not None and hasattr(listing_session, "close"):
            listing_session.close()

    equipos_activos = len(active_equipo_ids)
    predicciones_ok = 0
    predicciones_error = 0

    def _execute_prediction_for_equipo(equipo_id: int) -> bool:
        equipo_session = resolved_session_factory()
        if equipo_session is None or not hasattr(equipo_session, "close"):
            raise ValueError("session_factory debe retornar una sesión válida")

        try:
            execute_prediction(equipo_session, equipo_id)
            return True
        except HTTPException as exc:
            logger.warning(
                "Predicción periódica omitida equipo_id=%s detalle=%s",
                equipo_id,
                exc.detail,
            )
            return False
        except Exception:
            logger.exception(
                "Error inesperado ejecutando predicción periódica equipo_id=%s",
                equipo_id,
            )
            return False
        finally:
            equipo_session.close()

    scheduler_settings = get_settings()
    configured_workers = getattr(
        scheduler_settings, "prediction_scheduler_max_workers", 4
    )
    max_workers = (
        1
        if dialect_name == "sqlite"
        else max(
            1,
            min(configured_workers, equipos_activos or 1),
        )
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_execute_prediction_for_equipo, equipo_id): equipo_id
            for equipo_id in active_equipo_ids
        }

        for future in as_completed(futures):
            if future.result():
                predicciones_ok += 1
            else:
                predicciones_error += 1

    logger.info(
        "Ejecución periódica de predicciones finalizada activos=%d ok=%d error=%d",
        equipos_activos,
        predicciones_ok,
        predicciones_error,
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "equipos_activos": equipos_activos,
        "predicciones_ok": predicciones_ok,
        "predicciones_error": predicciones_error,
    }


def is_prediction_scheduler_running() -> bool:
    """Indica si el scheduler de predicciones está activo."""

    with _prediction_scheduler_lock:
        scheduler = _prediction_scheduler

    if scheduler is None:
        return False

    running = getattr(scheduler, "running", None)
    if isinstance(running, bool):
        return running

    started = getattr(scheduler, "started", None)
    if isinstance(started, bool):
        return started

    return False


def start_prediction_scheduler(session_factory: SessionFactory | None = None) -> bool:
    """Inicia scheduler de predicciones periódicas según configuración."""

    global _prediction_scheduler

    settings = get_settings()
    if not settings.enable_prediction_scheduler:
        logger.info("Scheduler de predicciones deshabilitado por configuración")
        return False

    if settings.prediction_interval_seconds <= 0:
        logger.warning(
            "Intervalo inválido para scheduler de predicciones: %s",
            settings.prediction_interval_seconds,
        )
        return False

    if BackgroundScheduler is None:
        logger.warning(
            "APScheduler no está disponible; se omite scheduler de predicciones"
        )
        return False

    resolved_session_factory = _resolve_session_factory(session_factory)
    if not callable(resolved_session_factory):
        logger.error(
            "SessionFactory inválido para scheduler de predicciones: %s",
            type(resolved_session_factory),
        )
        return False

    validation_session = None
    try:
        validation_session = resolved_session_factory()
    except Exception:
        logger.exception("SessionFactory falló al crear sesión para scheduler")
        return False

    if validation_session is None or not hasattr(validation_session, "close"):
        logger.error("SessionFactory no retornó una sesión válida")
        return False

    try:
        validation_session.close()
    except Exception:
        logger.warning(
            "No se pudo cerrar sesión de validación del scheduler de predicciones"
        )

    with _prediction_scheduler_lock:
        if _prediction_scheduler is not None:
            return True

        scheduler = BackgroundScheduler(timezone="UTC")
        try:
            scheduler.add_job(
                run_periodic_predictions,
                "interval",
                id=_PREDICTION_JOB_ID,
                seconds=settings.prediction_interval_seconds,
                max_instances=1,
                coalesce=True,
                replace_existing=True,
                kwargs={"session_factory": resolved_session_factory},
            )
            scheduler.start()
        except Exception:
            logger.exception("No se pudo crear/iniciar scheduler de predicciones")
            try:
                scheduler.shutdown(wait=False)
            except Exception:
                logger.warning("Fallo al limpiar scheduler parcialmente creado")
            return False

        _prediction_scheduler = scheduler

    logger.info(
        "Scheduler de predicciones iniciado job_id=%s (intervalo=%s segundos)",
        _PREDICTION_JOB_ID,
        settings.prediction_interval_seconds,
    )
    return True


def stop_prediction_scheduler() -> None:
    """Detiene scheduler de predicciones si está activo."""

    global _prediction_scheduler

    with _prediction_scheduler_lock:
        if _prediction_scheduler is None:
            return

        try:
            _prediction_scheduler.shutdown(wait=False)
        finally:
            _prediction_scheduler = None
