"""Middleware que registra métricas de latencia por endpoint."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class RequestMetricsMiddleware(BaseHTTPMiddleware):
    """Registra tiempo de respuesta y status code para cada request.

    Los logs incluyen correlation_id para trazabilidad cuando está disponible.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        correlation_id = getattr(request.state, "correlation_id", "-")

        # Import lazy para evitar el ciclo middleware -> router -> app. Las
        # métricas son observabilidad auxiliar: nunca deben romper el request.
        try:
            from app.routers.metrics import _record_metrics

            _record_metrics(request.url.path, elapsed_ms / 1000)
        except Exception:
            logger.debug("No se pudo registrar métrica de request", exc_info=True)

        logger.info(
            "metric=%s method=%s path=%s status=%s duration_ms=%.2f corr=%s",
            "request_duration",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            correlation_id,
        )

        return response
