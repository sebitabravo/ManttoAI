"""Endpoints de métricas y observabilidad."""

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
from app.middleware.rate_limit import limiter
from app.models.alerta import Alerta
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.usuario import Usuario

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Almacenamiento en memoria para métricas simples
# TODO: en despliegues con múltiples workers, cada proceso mantiene su propio
# estado en memoria. Para métricas agregadas consistentes, migrar a backend
# compartido/persistente (por ejemplo Redis).
_request_count: dict[str, int] = {}
_MAX_DURATION_SAMPLES_PER_ENDPOINT = 1000
_request_duration: dict[str, deque[float]] = {}
_active_users: set[int] = set()
_metrics_lock = RLock()


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

                # Registrar métricas (buffer acotado para evitar crecimiento infinito)
                with _metrics_lock:
                    _request_count[endpoint] = _request_count.get(endpoint, 0) + 1
                    _request_duration.setdefault(
                        endpoint,
                        deque(maxlen=_MAX_DURATION_SAMPLES_PER_ENDPOINT),
                    ).append(duration)

        return wrapper

    return decorator


def get_average_duration(endpoint: str, last_n: int = 100) -> float | None:
    """Retorna el tiempo promedio de respuesta para un endpoint."""

    with _metrics_lock:
        durations = _request_duration.get(endpoint)
        if durations:
            recent_durations = list(durations)[-last_n:]

    if not durations:
        return None

    # Deque no soporta slicing; se materializa un subconjunto acotado.
    if not recent_durations:
        return None

    return sum(recent_durations) / len(recent_durations)


@router.get("/summary")
@limiter.limit("6000/hour")
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

    with _metrics_lock:
        request_count_snapshot = dict(_request_count)

    # Métricas de API
    total_requests = sum(request_count_snapshot.values())

    # Calcular promedios de duración
    endpoint_metrics = {}
    for endpoint in request_count_snapshot.keys():
        avg_duration = get_average_duration(endpoint)
        endpoint_metrics[endpoint] = {
            "count": request_count_snapshot.get(endpoint, 0),
            "avg_duration_ms": round(avg_duration * 1000, 2) if avg_duration else None,
        }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
@limiter.limit("6000/hour")
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

    components["metrics"] = {
        "status": "healthy",
        "message": f"Tracking {_request_count.keys()} endpoints",
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
@limiter.limit("6000/hour")
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

    global _request_count, _request_duration, _active_users
    with _metrics_lock:
        _request_count.clear()
        _request_duration.clear()
        _active_users.clear()

    return {"message": "Métricas reseteadas exitosamente"}
