"""Middleware de detección y resolución de tenant (multi-tenant por subdominio o header)."""

import logging
from collections.abc import Callable

from fastapi import Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.database import SessionLocal
from app.models.organizacion import Organizacion

logger = logging.getLogger(__name__)

_LOCALHOST_ALIASES = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


def _create_session(request: Request) -> Session:
    """Entrega sesión DB compatible con runtime normal y tests."""

    testing_session_factory = getattr(request.app.state, "testing_session_local", None)
    if testing_session_factory is not None:
        return testing_session_factory()

    return SessionLocal()


def _extract_tenant_slug(request: Request) -> str | None:
    """Extrae tenant slug desde header X-Tenant-ID o subdominio.

    Prioridad:
    1. Header X-Tenant-ID (explícito, útil para APIs/proxies)
    2. Subdominio del host (ej: cliente-a.manttoai.com -> \"cliente-a\")

    Retorna None si no se detecta tenant (single-tenant fallback).
    """

    # 1. Header explícito
    tenant_header = request.headers.get("X-Tenant-ID")
    if tenant_header:
        slug = tenant_header.strip().lower()
        if slug:
            return slug

    # 2. Subdominio
    host = request.headers.get("host", "")
    host = host.split(":")[0].strip().lower()  # remover puerto

    if not host or host in _LOCALHOST_ALIASES:
        return None

    parts = host.split(".")
    # Requerimos al menos 3 partes: subdominio.dominio.tld
    if len(parts) >= 3:
        subdomain = parts[0]
        if subdomain and subdomain != "www":
            logger.debug("Tenant detectado por subdominio: %s", subdomain)
            return subdomain

    return None


def _resolve_tenant(request: Request) -> int | None:
    """Busca la Organizacion por slug y retorna su id.

    Si no se encuentra o falla la BD, retorna None (single-tenant fallback).
    Loggea warning cuando el slug no existe o está inactivo.
    """

    slug = _extract_tenant_slug(request)
    if slug is None:
        return None

    db: Session = _create_session(request)
    try:
        result = db.execute(
            select(Organizacion.id).where(
                Organizacion.slug == slug,
                Organizacion.is_active,
            )
        )
        org_id = result.scalar_one_or_none()

        if org_id is None:
            logger.warning("Tenant slug '%s' no encontrado o inactivo", slug)
            return None

        return org_id
    except Exception:
        logger.exception("Error al resolver tenant para slug '%s'", slug)
        return None
    finally:
        db.close()


async def tenant_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware que resuelve el tenant activo desde el subdominio o header.

    Guarda ``organizacion_id`` en ``request.state.tenant_id``.
    Si no se puede resolver, asigna ``None`` (comportamiento single-tenant
    para MVP, sin bloquear la request).
    """

    tenant_id = await run_in_threadpool(_resolve_tenant, request)
    request.state.tenant_id = tenant_id

    return await call_next(request)
