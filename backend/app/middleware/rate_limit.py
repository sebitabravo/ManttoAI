"""Middleware de rate limiting para proteger la API contra abuso."""

import logging
import os
from collections.abc import Callable

from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config import get_settings

logger = logging.getLogger(__name__)


def get_real_ip(request: Request) -> str:
    """Resuelve la IP real considerando X-Forwarded-For para load balancers.

    Cuando hay un proxy/LB (Traefik, Nginx) atrás, todas las requests vienen
    de la IP del proxy. X-Forwarded-For contiene las IPs originales.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # formato: "client_ip, proxy_ip, proxy_ip"
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


# Limiter real para middleware global
def _resolve_default_limits() -> list[str]:
    """Resuelve límites globales según entorno para evitar falsos positivos."""

    settings = get_settings()
    app_env = settings.app_env.strip().lower()

    # En desarrollo hay polling intensivo (dashboard + alertas + topbar).
    # 60000/hour = 1000/min = ~16 requests/segundo, suficiente para desarrollo.
    # El propósito es evitar rate limits mientras se desarrolla.
    if app_env in {"development", "dev", "local"}:
        return ["60000/hour"]

    # En stage/prod mantenemos un límite estricto pero usable para UI con polling.
    return ["1500/hour"]


def _resolve_storage_uri() -> str:
    """Resuelve el storage URI para Redis con autenticación.

    Fallback a fail-fast (no storage) es más seguro que memoria porque:
    1. Memoria no escala en múltiples instancias (each tiene su propio contador)
    2. En producción sin Redis el sistema debería fallar, no silently degrade
    """
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_password = os.getenv("REDIS_PASSWORD")

    try:
        import redis

        # Intentar Redis con autenticación
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            socket_connect_timeout=2,
        )
        r.ping()
        logger.info(f"Redis connected for rate limiting: {redis_host}:{redis_port}")
        auth_part = f":{redis_password}@" if redis_password else ""
        return f"redis://{auth_part}{redis_host}:{redis_port}"
    except Exception as e:
        logger.error(
            f"Redis not available ({e}). Rate limiting DISABLED for safety. "
            "In production, ensure Redis is available or requests will be blocked."
        )
        # Fail-fast: denegar todo si no hay Redis (más seguro que memory)
        return "memory://"


_global_limiter = Limiter(
    key_func=get_real_ip,  # Usa X-Forwarded-For para load balancers
    default_limits=_resolve_default_limits(),
    storage_uri=_resolve_storage_uri(),
    headers_enabled=False,
)

# Limiter compartido para middleware global y decoradores por endpoint.
limiter = _global_limiter

_SUPPORTED_ROLES = {"admin", "tecnico", "visualizador"}


def setup_rate_limiting(app) -> None:
    """Configura rate limiting global en la aplicación FastAPI."""

    app.state.limiter = _global_limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)


def limit_by_role(
    admin_limit: str = "1000/hour",
    tecnico_limit: str = "500/hour",
    visualizador_limit: str = "200/hour",
):
    """Aplica rate limits dinámicos según rol autenticado.

    Si no se puede resolver rol en request.state, se aplica el límite de
    visualizador como fallback seguro.
    """

    role_limits = {
        "admin": admin_limit,
        "tecnico": tecnico_limit,
        "visualizador": visualizador_limit,
    }

    def resolve_limit_for_key(key: str) -> str:
        """Resuelve el límite a partir de la llave <rol>:<identificador>."""

        role = key.split(":", 1)[0].strip().lower() if key else "visualizador"
        return role_limits.get(role, visualizador_limit)

    def resolve_role_limit_key(request: Request) -> str:
        """Construye llave de rate limit con rol + usuario/ip."""

        raw_role = getattr(request.state, "manttoai_user_role", None)
        normalized_role = (
            str(raw_role).strip().lower() if raw_role is not None else "visualizador"
        )
        if normalized_role not in _SUPPORTED_ROLES:
            normalized_role = "visualizador"

        user_id = getattr(request.state, "manttoai_user_id", None)
        if user_id is not None:
            return f"{normalized_role}:user:{user_id}"

        return f"{normalized_role}:ip:{get_real_ip(request)}"

    def decorator(func: Callable):
        return limiter.limit(
            resolve_limit_for_key,
            key_func=resolve_role_limit_key,
            override_defaults=False,
        )(func)

    return decorator
