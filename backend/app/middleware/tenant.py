"""Middleware de identificacion de tenant via header X-Tenant-ID."""

import logging

from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class TenantMiddleware:
    """Middleware que extrae el tenant ID del header X-Tenant-ID y lo
    almacena en request.state.tenant_id para uso en toda la cadena de
    handlers, servicios y repositorios.

    El tenant ID es opcional. Si no se provee, tenant_id queda como None
    (comportamiento single-tenant / default).

    Uso esperado:
        app.add_middleware(TenantMiddleware)
        # Luego en cualquier handler:
        tenant_id = request.state.tenant_id
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        from starlette.requests import Request  # noqa: PLC0415

        request = Request(scope, receive=receive)

        tenant_id = request.headers.get("X-Tenant-ID")

        if tenant_id is not None:
            try:
                parsed = int(tenant_id)
            except (ValueError, TypeError):
                logger.warning(
                    "X-Tenant-ID header invalido: '%s'. Se ignora.", tenant_id
                )
                parsed = None

            request.state.tenant_id = parsed
        else:
            request.state.tenant_id = None

        await self.app(scope, receive, send)
