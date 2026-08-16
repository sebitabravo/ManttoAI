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
from ipaddress import ip_address, ip_network
from collections.abc import Callable
from urllib.parse import quote, urlparse, urlunparse

from fastapi import Request
from fastapi.responses import Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config import get_settings

logger = logging.getLogger(__name__)


def get_real_ip(request: Request) -> str:
    """Resuelve la IP sin confiar en headers enviados por clientes arbitrarios."""

    peer = get_remote_address(request)
    forwarded = request.headers.get("X-Forwarded-For")
    if not forwarded:
        return peer

    trusted_networks = []
    for raw_network in get_settings().trusted_proxy_ips.split(","):
        raw_network = raw_network.strip()
        if not raw_network:
            continue
        try:
            trusted_networks.append(ip_network(raw_network, strict=False))
        except ValueError:
            logger.warning("Red de proxy confiable inválida: %s", raw_network)

    try:
        peer_ip = ip_address(peer)
    except ValueError:
        return peer

    if not any(peer_ip in network for network in trusted_networks):
        return peer

    # X-Forwarded-For se ordena cliente -> proxy más cercano. Recorremos desde
    # el proxy conocido hacia atrás y tomamos el primer salto no confiable.
    for raw_hop in reversed(forwarded.split(",")):
        try:
            candidate = ip_address(raw_hop.strip())
        except ValueError:
            continue
        if not any(candidate in network for network in trusted_networks):
            return str(candidate)

    return peer


def resolve_api_limit() -> str:
    """Configurable limit for API endpoints.

    Set via RATE_LIMIT_API env var.
    Dev: 60000/hour (1000/min, enough for polling)
    Prod: 1500/hour (25/min, stricter)
    """
    settings = get_settings()
    app_env = settings.app_env.strip().lower()

    default_limit = (
        "60000/hour" if app_env in {"development", "dev", "local"} else "1500/hour"
    )
    return os.getenv("RATE_LIMIT_API", default_limit)


def _resolve_default_limits() -> list[str]:
    """Resolves global limits by environment.

    Uses RATE_LIMIT_API consistently.
    """

    return [resolve_api_limit()]


def _resolve_storage_uri() -> str:
    """Retorna el backend de almacenamiento sin hacer I/O durante el import."""

    settings = get_settings()
    redis_url = settings.redis_url.strip()
    if not redis_url:
        logger.info("REDIS_URL no configurado; rate limiting usará memoria local.")
        return "memory://"

    parsed = urlparse(redis_url)
    if parsed.scheme not in {"redis", "rediss"} or not parsed.hostname:
        logger.warning("REDIS_URL inválido; rate limiting usará memoria local.")
        return "memory://"

    # REDIS_PASSWORD puede venir separado en Compose. Construimos una URI
    # válida sin probar la red: RedisStorage resolverá la conexión al usarla.
    password = settings.redis_password or parsed.password
    if settings.redis_password and not parsed.password:
        username = quote(parsed.username or "", safe="")
        host = parsed.hostname
        port = f":{parsed.port}" if parsed.port else ""
        auth = (
            f"{username}:{quote(password, safe='')}@"
            if username
            else f":{quote(password, safe='')}@"
        )
        redis_url = urlunparse(
            (
                parsed.scheme,
                f"{auth}{host}{port}",
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

    logger.info("Rate limiting configurado con almacenamiento Redis.")
    return redis_url


_global_limiter = Limiter(
    key_func=get_real_ip,
    default_limits=_resolve_default_limits(),
    storage_uri=_resolve_storage_uri(),
    headers_enabled=False,
)

limiter = _global_limiter


def get_api_limit() -> str:
    """Alias for resolve_api_limit()."""
    return resolve_api_limit()


SUPPORTED_ROLES = {"admin", "tecnico", "visualizador"}


def _rate_limit_logged_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handler que logea antes de delegar al handler por defecto."""
    logger.warning(
        "Rate limit triggered for %s on %s %s",
        request.client.host if request.client else "unknown",
        request.method,
        request.url.path,
    )
    return _rate_limit_exceeded_handler(request, exc)


def setup_rate_limiting(app) -> None:
    """Configura rate limiting global en la aplicacion FastAPI."""

    app.state.limiter = _global_limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_logged_handler)
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
