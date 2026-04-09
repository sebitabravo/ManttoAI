"""Middleware de rate limiting para proteger la API contra abuso."""

from collections.abc import Callable

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config import get_settings


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


_global_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=_resolve_default_limits(),
    storage_uri="memory://",
    headers_enabled=False,
)

# Limiter compartido para middleware global y decoradores por endpoint.
limiter = _global_limiter


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
    """Decorator no-op mantenido por compatibilidad de imports."""

    def decorator(func: Callable):
        return func

    return decorator
