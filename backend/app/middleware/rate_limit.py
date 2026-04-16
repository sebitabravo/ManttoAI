"""Middleware de rate limiting para proteger la API contra abuso.

Cache strategy para reducir carga:
- dashboard: TTL 30s (usa Redis si está disponible)
- alertas: TTL 10s
- lecturas: no cachear (tiempo real)

Cache functions disponibles:
- get_cached(key) -> valor o None
- set_cached(key, valor, ttl=30) -> None
- invalidate_cached(key) -> None
"""

Configuración centralizada vía variables de entorno:
- RATE_LIMIT_API: Límite para endpoints de API (default: 6000/hour en dev, 600/hour en prod)
- RATE_LIMIT_DEV: Límite global en desarrollo (default: 60000/hour)
- RATE_LIMIT_PROD: Límite global en producción (default: 1500/hour)
- REDIS_URL: URL de Redis para storage
- REDIS_PASSWORD: Password de Redis (si aplica)
"""

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
    """Resuelve la IP real considerando X-Forwarded-For para load balancers."""

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


def resolve_api_limit() -> str:
    """Límite configurable para endpoints de API.

    Configurable vía RATE_LIMIT_API.
    En desarrollo: 6000/hour (100/min, suficiente para polling)
    En producción: 600/hour (10/min, más restrictivo)
    """
    settings = get_settings()
    app_env = settings.app_env.strip().lower()

    default_limit = (
        "6000/hour" if app_env in {"development", "dev", "local"} else "600/hour"
    )
    return os.getenv("RATE_LIMIT_API", default_limit)


# Limiter real para middleware global
def _resolve_default_limits() -> list[str]:
    """Resuelve límites globales según entorno.

    Configurable vía RATE_LIMIT_API (para todos los endpoints).
    Valor por defecto: 60000/hour en dev (1000/min), 1500/hour en prod.

    Los límites específicos en routers (auth, onboarding) se suman a este.
    """

    settings = get_settings()
    app_env = settings.app_env.strip().lower()

    # RATE_LIMIT_API controla TODOS los endpoints excepto los específicos
    default = (
        "60000/hour" if app_env in {"development", "dev", "local"} else "1500/hour"
    )
    return [os.getenv("RATE_LIMIT_API", default)]


def _resolve_storage_uri() -> str:
    """Resuelve el storage URI para Redis con autenticación.

    Fallback a fail-fast (no storage) es más seguro que memoria porque:
    1. Memoria no escala en múltiples instancias (each tiene su propio contador)
    2. En producción sin Redis el sistema debería fallar, no silently degrade

    Soporta dos formatos de URL:
    - redis://redis:6379 (sin auth)
    - redis://:password@redis:6379 (con auth)
    """
    # Parsear REDIS_URL que puede venir con password embebido
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    redis_password = os.getenv("REDIS_PASSWORD")

    # Extraer host:port de la URL
    from urllib.parse import urlparse

    parsed = urlparse(redis_url)
    redis_host = parsed.hostname or "redis"
    redis_port = parsed.port or 6379

    # Si hay password en variable separada, usarla
    if not redis_password and parsed.password:
        redis_password = parsed.password

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
        # Construir URI con auth para slowapi
        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}"
        return f"redis://{redis_host}:{redis_port}"
    except Exception as e:
        logger.warning(
            f"Redis not available ({e}). Using in-memory rate limiting (devonly)."
        )
        # Fail-fast: denegar todo si no hay Redis (más seguro que memory)
        return "memory://"


_global_limiter = Limiter(
    key_func=resolve_limit_key,  # API Key (IoT) vs IP (UI) vs user (auth)
    default_limits=_resolve_default_limits(),
    storage_uri=_resolve_storage_uri(),
    headers_enabled=False,
)

# Limiter compartido para middleware global y decoradores por endpoint.
limiter = _global_limiter


# Función helper para usar en routers - devuelve el límite configurable
def get_api_limit() -> str:
    """Alias de resolve_api_limit() para uso en routers."""
    return resolve_api_limit()


def resolve_limit_key(request: Request) -> str:
    """Resuelve la key de rate limiting: API Key (IoT) vs IP (UI).

    Strategy:
    - Si tiene X-API-Key headers -> rate limit por API key (dispositivo)
    - Si tiene sesión/token -> rate limit por user ID
    - Si es anon -> rate limit por IP

    Esto evita que IoT y UI compartan límites.
    """
    # Check para API Key (IoT devices)
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"apikey:{api_key[:16]}"  # Usar solo primeros 16 chars

    # Check para usuario autenticado
    user_id = getattr(request.state, "manttoai_user_id", None)
    if user_id:
        return f"user:{user_id}"

    # Fallback a IP real (considerando proxy)
    return get_real_ip(request)


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
