"""Middleware automático de audit logging."""

import logging
from collections.abc import Callable

from fastapi import HTTPException
from fastapi import Request, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.database import SessionLocal
from app.dependencies import get_current_user
from app.services.audit_service import log_audit

logger = logging.getLogger(__name__)

_SENSITIVE_GET_PREFIXES = {
    "/api/v1/usuarios",
    "/api/v1/api-keys",
    "/api/v1/reportes",
    "/usuarios",
    "/api-keys",
    "/reportes",
}


def _should_audit_request(method: str, path: str) -> bool:
    """Define qué requests se auditan para balancear señal/ruido."""

    normalized_method = method.upper()
    normalized_path = path.rstrip("/") or "/"

    if normalized_method in {"POST", "PUT", "PATCH", "DELETE"}:
        return True

    if normalized_method == "GET":
        return any(
            normalized_path.startswith(prefix) for prefix in _SENSITIVE_GET_PREFIXES
        )

    return False


def _create_session(request: Request) -> Session:
    """Entrega sesión DB compatible con runtime normal y tests."""

    testing_session_factory = getattr(request.app.state, "testing_session_local", None)
    if testing_session_factory is not None:
        return testing_session_factory()

    return SessionLocal()


def _resolve_user_id_and_log(
    request: Request,
    action: str,
    entity_type: str,
    entity_id: int | None,
    response_status: int,
) -> None:
    """Resuelve usuario y persiste auditoría usando una única sesión DB."""

    user_id: int | None = None
    audit_db: Session = _create_session(request)
    try:
        try:
            user = get_current_user(request, None, audit_db)
            user_id = user.id
        except HTTPException as exc:
            # Casos esperados: request sin sesión o con credenciales inválidas.
            if exc.status_code in {401, 403}:
                logger.debug("Usuario no autenticado para auditoría: %s", exc.detail)
                user_id = None
            else:
                logger.exception(
                    "HTTPException inesperada al resolver usuario para auditoría"
                )
                user_id = None
        except (RuntimeError, TypeError, ValueError, SQLAlchemyError):
            logger.exception("Error inesperado al resolver usuario para auditoría")
            user_id = None

        if entity_type != "unknown" and (user_id is not None or entity_type == "auth"):
            log_audit(
                db=audit_db,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                new_values={
                    "request_path": request.url.path,
                    "http_method": request.method,
                    "response_status": response_status,
                },
                usuario_id=user_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
    except SQLAlchemyError:
        # No fallar el request si el audit log falla
        logger.exception("Fallo al escribir audit log")
    finally:
        audit_db.close()


async def audit_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware que registra automáticamente acciones de auditoría.

    Registra:
    - POST, PUT, DELETE, PATCH requests
    - Usuario autenticado (si existe)
    - IP address y user agent
    - Response status code
    """

    if not _should_audit_request(request.method, request.url.path):
        return await call_next(request)

    response = await call_next(request)

    # Determinar acción y entidad basado en la ruta y método
    action = _get_action_from_method(request.method, request.url.path)
    entity_type, entity_id = _get_entity_from_path(request.url.path)

    if entity_type == "unknown":
        return response

    # Resolver usuario + persistir auditoría en threadpool (una sola sesión DB).
    await run_in_threadpool(
        _resolve_user_id_and_log,
        request,
        action,
        entity_type,
        entity_id,
        response.status_code,
    )

    return response


def _get_action_from_method(method: str, path: str) -> str:
    """Mapea método HTTP a acción de auditoría."""

    normalized_path = path.rstrip("/").lower()
    normalized_method = method.upper()

    if normalized_method == "POST" and normalized_path.endswith("/auth/login"):
        return "login"
    if normalized_method == "POST" and normalized_path.endswith("/auth/logout"):
        return "logout"
    if normalized_method == "POST" and normalized_path.endswith("/auth/register"):
        return "register"

    mapping = {
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
        "GET": "read",
    }
    return mapping.get(normalized_method, normalized_method.lower())


def _get_entity_from_path(path: str) -> tuple[str, int | None]:
    """
    Extrae tipo de entidad y ID desde la ruta.

    Ejemplos:
    - /api/v1/equipos -> ("equipo", None)
    - /api/v1/equipos/123 -> ("equipo", 123)
    - /api/v1/usuarios/456 -> ("usuario", 456)
    """

    normalized_path = path.rstrip("/") or "/"

    # Mapeo de rutas a entidades
    path_mapping = {
        "/api/v1/equipos": "equipo",
        "/equipos": "equipo",
        "/api/v1/usuarios": "usuario",
        "/usuarios": "usuario",
        "/api/v1/alertas": "alerta",
        "/alertas": "alerta",
        "/api/v1/umbrales": "umbral",
        "/umbrales": "umbral",
        "/api/v1/mantenciones": "mantencion",
        "/mantenciones": "mantencion",
        "/api/v1/lecturas": "lectura",
        "/lecturas": "lectura",
        "/api/v1/predicciones": "prediccion",
        "/predicciones": "prediccion",
        "/api/v1/api-keys": "api_key",
        "/api-keys": "api_key",
        "/api/v1/reportes": "reporte",
        "/reportes": "reporte",
        "/auth": "auth",
        "/api/v1/auth": "auth",
        "/api/v1/iot": "iot",
    }

    segments = [segment for segment in normalized_path.split("/") if segment]

    # Buscar coincidencia de ruta
    for route, entity_type in path_mapping.items():
        route_segments = [segment for segment in route.split("/") if segment]
        if segments[: len(route_segments)] == route_segments:
            if len(segments) > len(route_segments):
                candidate = segments[len(route_segments)]
                try:
                    return entity_type, int(candidate)
                except ValueError:
                    pass

            return entity_type, None

    return "unknown", None
