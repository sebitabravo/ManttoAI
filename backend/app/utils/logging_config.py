"""Configuración centralizada de logging estructurado."""

import logging
import sys
from datetime import datetime, timezone

from pythonjsonlogger import jsonlogger


def setup_logging(app_name: str = "ManttoAI", level: str = "INFO") -> None:
    """Configura logging estructurado JSON para la aplicación."""

    logger = logging.getLogger()
    if logger.handlers:
        logger.setLevel(getattr(logging, level.upper()))
        return

    logger.setLevel(getattr(logging, level.upper()))

    # Handler para stdout con formato JSON
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        timestamp=True,
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Suprimir loggers verbosos de terceros
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: int | None = None,
    ip_address: str | None = None,
) -> None:
    """Registra información de request HTTP."""

    logger = logging.getLogger("api.request")

    log_data = {
        "event": "http_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "user_id": user_id,
        "ip_address": ip_address,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(log_data)


def log_error(
    error: Exception,
    context: dict | None = None,
    user_id: int | None = None,
) -> None:
    """Registra errores con contexto adicional."""

    logger = logging.getLogger("api.error")

    log_data = {
        "event": "error",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    logger.error(log_data, exc_info=True)


def log_business_event(
    event_type: str,
    entity_type: str,
    entity_id: int | None = None,
    user_id: int | None = None,
    metadata: dict | None = None,
) -> None:
    """Registra eventos de negocio."""

    logger = logging.getLogger("business.event")

    log_data = {
        "event": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "user_id": user_id,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(log_data)
