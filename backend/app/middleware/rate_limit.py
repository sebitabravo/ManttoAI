"""Middleware de rate limiting para proteger la API contra abuso.

Centralized config via env vars:
- RATE_LIMIT_API: limit for API endpoints (default: 60000/hour dev, 1500/hour prod)
- REDIS_URL: URL for Redis storage
- REDIS_PASSWORD: Redis password if needed

Cache strategy:
- dashboard: TTL 30s
- alertas: TTL 10s
- lecturas: no cache (real-time)
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
    """Resolves real IP considering X-Forwarded-For for load balancers."""

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


def resolve_api_limit() -> str:
    """Configurable limit for API endpoints.

    Set via RATE_LIMIT_API env var.
    Dev: 6000/hour (100/min, enough for polling)
    Prod: 600/hour (10/min, stricter)
    """
    settings = get_settings()
    app_env = settings.app_env.strip().lower()

    default_limit = (
        "6000/hour" if app_env in {"development", "dev", "local"} else "600/hour"
    )
    return os.getenv("RATE_LIMIT_API", default_limit)


def _resolve_default_limits() -> list[str]:
    """Resolves global limits by environment.

    RATE_LIMIT_API controls all endpoints.
    """

    settings = get_settings()
    app_env = settings.app_env.strip().lower()

    default = (
        "60000/hour" if app_env in {"development", "dev", "local"} else "1500/hour"
    )
    return [os.getenv("RATE_LIMIT_API", default)]


def _resolve_storage_uri() -> str:
    """Resolves storage URI for Redis with auth.

    Falls back to memory only in dev.
    """
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    redis_password = os.getenv("REDIS_PASSWORD")

    from urllib.parse import urlparse

    parsed = urlparse(redis_url)
    redis_host = parsed.hostname or "redis"
    redis_port = parsed.port or 6379

    if not redis_password and parsed.password:
        redis_password = parsed.password

    try:
        import redis

        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            socket_connect_timeout=2,
        )
        r.ping()
        logger.info(f"Redis connected for rate limiting: {redis_host}:{redis_port}")
        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}"
        return f"redis://{redis_host}:{redis_port}"
    except Exception as e:
        logger.warning(f"Redis not available ({e}). Using in-memory rate limiting.")
        return "memory://"


_global_limiter = Limiter(
    key_func=get_real_ip,  # use X-Forwarded-For for load balancers
    default_limits=_resolve_default_limits(),
    storage_uri=_resolve_storage_uri(),
    headers_enabled=False,
)

limiter = _global_limiter


def get_api_limit() -> str:
    """Alias for resolve_api_limit()."""
    return resolve_api_limit()


SUPPORTED_ROLES = {"admin", "tecnico", "visualizador"}


def setup_rate_limiting(app) -> None:
    """Configura rate limiting global en la aplicacion FastAPI."""

    app.state.limiter = _global_limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)


def limit_by_role(
    admin_limit: str = "1000/hour",
    tecnico_limit: str = "500/hour",
    visualizador_limit: str = "200/hour",
):
    """Aplica rate limits dinamicos segun rol autenticado.

    Si no se puede resolver rol en request.state, se aplica el limite de
    visualizador como fallback seguro.
    """

    role_limits = {
        "admin": admin_limit,
        "tecnico": tecnico_limit,
        "visualizador": visualizador_limit,
    }

    def resolve_limit_for_key(key: str) -> str:
        """Resuelve el limite a partir de la llave <rol>:<identificador>."""

        role = key.split(":", 1)[0].strip().lower() if key else "visualizador"
        return role_limits.get(role, visualizador_limit)

    def resolve_role_limit_key(request: Request) -> str:
        """Construye llave de rate limit con rol + usuario/ip."""

        raw_role = getattr(request.state, "manttoai_user_role", None)
        normalized_role = (
            str(raw_role).strip().lower() if raw_role is not None else "visualizador"
        )
        if normalized_role not in SUPPORTED_ROLES:
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
