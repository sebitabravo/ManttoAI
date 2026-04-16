"""Middleware de rate limiting para proteger la API contra abuso."""

import logging
from collections.abc import Callable

from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config import get_settings

logger = logging.getLogger(__name__)


# Limiter real para middleware global
def _resolve_default_limits() -> list[str]:
    """Resuelve límites globales según entorno para evitar falsos positivos."""

    settings = get_settings()
    app_env = settings.app_env.strip().lower()

    # En desarrollo hay polling intensivo (dashboard + alertas + topbar),
    # por lo que 200/hour genera 429 falsos en uso normal.
    if app_env in {"development", "dev", "local"}:
        return ["5000/hour"]

    # En stage/prod mantenemos un límite estricto pero usable para UI con polling.
    return ["1500/hour"]


def _resolve_storage_uri() -> str:
    """Resuelve el storage URI intentando Redis, con fallback a memoria."""
    try:
        # Intentar Redis si está disponible
        import redis

        r = redis.Redis(host="redis", port=6379, socket_connect_timeout=1)
        r.ping()
        logger.info("Using Redis for rate limiting storage")
        return "redis://redis:6379"
    except Exception as e:
        logger.warning(
            f"Redis not available ({e}), using in-memory storage for rate limiting"
        )
        return "memory://"


_global_limiter = Limiter(
    key_func=get_remote_address,
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

        return f"{normalized_role}:ip:{get_remote_address(request)}"

    def decorator(func: Callable):
        return limiter.limit(
            resolve_limit_for_key,
            key_func=resolve_role_limit_key,
            override_defaults=False,
        )(func)

    return decorator
