"""Endpoints de métricas y observabilidad."""

import json
import logging
from collections import deque
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from functools import wraps
from threading import RLock
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.alerta import Alerta
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.usuario import Usuario

router = APIRouter(prefix="/metrics", tags=["metrics"])
logger = logging.getLogger(__name__)

# Tamaño máximo de muestras de duración por endpoint
_MAX_DURATION_SAMPLES = 1000

# Fallback en memoria (cuando Redis no está disponible)
_mem_request_count: dict[str, int] = {}
_mem_request_duration: dict[str, deque[float]] = {}
_mem_lock = RLock()

# Cliente Redis (lazy init)
_redis_client = None


def _get_redis():
    """Obtiene cliente Redis con lazy initialization y fallback graceful."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        import redis as redis_lib
        from app.config import get_settings

        settings = get_settings()
        _redis_client = redis_lib.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password or None,
            socket_connect_timeout=1,
            decode_responses=True,
        )
        # Verificar conexion
        _redis_client.ping()
        logger.info("Métricas conectadas a Redis %s:%s", settings.redis_host, settings.redis_port)
        return _redis_client
    except Exception:
        # Fallback a memoria si Redis no está disponible
        _redis_client = None
        return None


# Claves Redis
_METRICS_PREFIX = "manttoai:metrics"
_COUNT_KEY = f"{_METRICS_PREFIX}:count"
_DURATION_KEY = f"{_METRICS_PREFIX}:duration"


def track_request_metrics(
    endpoint: str,
) -> Callable:
    """Decorator para rastrear métricas de requests."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = perf_counter() - start_time
                _record_metrics(endpoint, duration)

        return wrapper

    return decorator


def _record_metrics(endpoint: str, duration: float) -> None:
    """Registra métricas en Redis (preferred) o memoria (fallback)."""
    r = _get_redis()

    if r is not None:
        try:
            pipe = r.pipeline()
            pipe.hincrby(_COUNT_KEY, endpoint, 1)
            # Almacenar duración como JSON en lista acotada
            duration_key = f"{_DURATION_KEY}:{endpoint}"
            pipe.lpush(duration_key, json.dumps({"d": round(duration, 6), "t": datetime.now(timezone.utc).isoformat()}))
            pipe.ltrim(duration_key, 0, _MAX_DURATION_SAMPLES - 1)
            pipe.execute()
            return
        except Exception:
            logger.debug("Fallback a métricas en memoria para endpoint=%s", endpoint)

    # Fallback en memoria
    with _mem_lock:
        _mem_request_count[endpoint] = _mem_request_count.get(endpoint, 0) + 1
        _mem_request_duration.setdefault(
            endpoint,
            deque(maxlen=_MAX_DURATION_SAMPLES),
        ).append(duration)


def _get_all_counts() -> dict[str, int]:
    """Obtiene contadores desde Redis o memoria."""
    r = _get_redis()

    if r is not None:
        try:
            raw = r.hgetall(_COUNT_KEY)
            return {k: int(v) for k, v in raw.items()} if raw else {}
        except Exception:
            pass

    with _mem_lock:
        return dict(_mem_request_count)


def _get_average_duration(endpoint: str, last_n: int = 100) -> float | None:
    """Retorna el tiempo promedio de respuesta para un endpoint."""
    r = _get_redis()

    if r is not None:
        try:
            duration_key = f"{_DURATION_KEY}:{endpoint}"
            samples = r.lrange(duration_key, 0, last_n - 1)
            if not samples:
                return None
            durations = [json.loads(s)["d"] for s in samples]
            return sum(durations) / len(durations)
        except Exception:
            pass

    # Fallback en memoria
    with _mem_lock:
        durations = _mem_request_duration.get(endpoint)
        if not durations:
            return None
        recent = list(durations)[-last_n:]
        return sum(recent) / len(recent) if recent else None


@router.get("/summary")
async def get_metrics_summary(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Retorna un resumen de métricas del sistema."""

    # Métricas de base de datos
    total_equipos = db.scalar(select(func.count(Equipo.id)))
    total_alertas_activas = db.scalar(
        select(func.count(Alerta.id)).where(Alerta.leida.is_(False))
    )
    total_lecturas_24h = db.scalar(
        select(func.count(Lectura.id)).where(
            Lectura.timestamp >= datetime.now(timezone.utc) - timedelta(hours=24)
        )
    )
    total_usuarios = db.scalar(select(func.count(Usuario.id)))

    request_count_snapshot = _get_all_counts()

    # Métricas de API
    total_requests = sum(request_count_snapshot.values())

    # Calcular promedios de duración
    endpoint_metrics = {}
    for endpoint in request_count_snapshot.keys():
        avg_duration = _get_average_duration(endpoint)
        endpoint_metrics[endpoint] = {
            "count": request_count_snapshot.get(endpoint, 0),
            "avg_duration_ms": round(avg_duration * 1000, 2) if avg_duration else None,
        }

    # Backend de métricas activo
    r = _get_redis()
    metrics_backend = "redis" if r is not None else "memory"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics_backend": metrics_backend,
        "system": {
            "total_equipos": total_equipos or 0,
            "total_alertas_activas": total_alertas_activas or 0,
            "total_lecturas_24h": total_lecturas_24h or 0,
            "total_usuarios": total_usuarios or 0,
        },
        "api": {
            "total_requests": total_requests,
            "endpoints": endpoint_metrics,
        },
    }


@router.get("/health-detailed")
async def get_detailed_health(
    request: Request,
    db: Session = Depends(get_db),
):
    """Retorna un health check detallado con múltiples componentes."""

    components = {}

    # Verificar base de datos
    try:
        db.execute(select(1).limit(1))
        components["database"] = {
            "status": "healthy",
            "message": "Database connection OK",
        }
    except SQLAlchemyError as exc:
        components["database"] = {"status": "unhealthy", "message": str(exc)}

    # Verificar Redis
    r = _get_redis()
    if r is not None:
        try:
            r.ping()
            components["redis"] = {"status": "healthy", "message": "Redis connection OK"}
        except Exception as exc:
            components["redis"] = {"status": "unhealthy", "message": str(exc)}
    else:
        components["redis"] = {"status": "degraded", "message": "Redis unavailable, using in-memory fallback"}

    endpoints_tracked = list(_get_all_counts().keys())
    components["metrics"] = {
        "status": "healthy",
        "message": f"Tracking {len(endpoints_tracked)} endpoints",
        "backend": "redis" if r else "memory",
    }

    # Determinar estado general
    all_healthy = all(c["status"] == "healthy" for c in components.values())
    overall_status = "healthy" if all_healthy else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": components,
    }


@router.post("/reset")
async def reset_metrics(
    request: Request,
    current_user=Depends(get_current_user),
):
    """Reseta las métricas acumuladas (solo admin)."""

    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin puede resetear métricas",
        )

    # Limpiar Redis
    r = _get_redis()
    if r is not None:
        try:
            # Eliminar claves de métricas
            count_keys = r.hkeys(_COUNT_KEY)
            if count_keys:
                pipe = r.pipeline()
                pipe.delete(_COUNT_KEY)
                for key in count_keys:
                    pipe.delete(f"{_DURATION_KEY}:{key}")
                pipe.execute()
        except Exception:
            pass

    # Limpiar memoria siempre (por si hay datos residuales)
    global _mem_request_count, _mem_request_duration
    with _mem_lock:
        _mem_request_count.clear()
        _mem_request_duration.clear()

    return {"message": "Métricas reseteadas exitosamente"}
