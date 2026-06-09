"""Middleware que asigna correlation ID a cada request."""

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Agrega X-Correlation-ID a cada request/response.

    Si el cliente ya envía un correlation ID en el header, se reutiliza.
    Si no, se genera uno nuevo via uuid4. Queda disponible en
    request.state.correlation_id para tracing en servicios.
    """

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get(
            "X-Correlation-ID", str(uuid.uuid4())
        )
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
