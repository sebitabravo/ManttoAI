"""Endpoints de métricas y observabilidad."""

from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from time import perf_counter
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.middleware.rate_limit import limiter
from app.models.alerta import Alerta
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.usuario import Usuario
from app.utils.logging_config import setup_logging

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Almacenamiento en memoria para métricas simples
_request_count: dict[str, int] = {}
_request_duration: dict[str, list[float]] = {}
_active_users: set[int] = set()


def track_request_metrics(
    endpoint: str,
) -> Callable:
    """Decorator para rastrear métricas de requests."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = perf_counter()
            try:
                result = await func(*args, **kwargs)
                duration = perf_counter() - start_time

                # Registrar métricas
                _request_count[endpoint] = _request_count.get(endpoint, 0) + 1
                _request_duration.setdefault(endpoint, []).append(duration)

                return result
            except Exception as e:
                duration = perf_counter() - start_time
                _request_count[endpoint] = _request_count.get(endpoint, 0) + 1
                _request_duration.setdefault(endpoint, []).append(duration)
                raise

        return wrapper

    return decorator


def get_average_duration(endpoint: str, last_n: int = 100) -> float | None:
    """Retorna el tiempo promedio de respuesta para un endpoint."""

    durations = _request_duration.get(endpoint, [])
    if not durations:
        return None

    # Solo considerar los últimos N requests
    recent_durations = durations[-last_n:]
    return sum(recent_durations) / len(recent_durations)


@router.get("/summary")
@limiter.limit("200/hour")
async def get_metrics_summary(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Retorna un resumen de métricas del sistema."""

    # Métricas de base de datos
    total_equipos = db.scalar(select(func.count(Equipo.id)))
    total_alertas_activas = db.scalar(
        select(func.count(Alerta.id)).where(Alerta.activa == True)
    )
    total_lecturas_24h = db.scalar(
        select(func.count(Lectura.id)).where(
            Lectura.timestamp >= datetime.utcnow() - timedelta(hours=24)
        )
    )
    total_usuarios = db.scalar(select(func.count(Usuario.id)))

    # Métricas de API
    total_requests = sum(_request_count.values())

    # Calcular promedios de duración
    endpoint_metrics = {}
    for endpoint in _request_count.keys():
        avg_duration = get_average_duration(endpoint)
        endpoint_metrics[endpoint] = {
            "count": _request_count.get(endpoint, 0),
            "avg_duration_ms": round(avg_duration * 1000, 2) if avg_duration else None,
        }

    return {
        "timestamp": datetime.utcnow().isoformat(),
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
@limiter.limit("500/hour")  # Health checks se llaman mucho
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
    except Exception as e:
        components["database"] = {"status": "unhealthy", "message": str(e)}

    # Verificar contador de métricas
    try:
        components["metrics"] = {
            "status": "healthy",
            "message": f"Tracking {_request_count.keys()} endpoints",
        }
    except Exception as e:
        components["metrics"] = {"status": "unhealthy", "message": str(e)}

    # Determinar estado general
    all_healthy = all(c["status"] == "healthy" for c in components.values())
    overall_status = "healthy" if all_healthy else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "components": components,
    }


@router.post("/reset")
@limiter.limit("20/hour")  # Resetear métricas es sensible
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
    _request_count.clear()
    _request_duration.clear()
    _active_users.clear()

    return {"message": "Métricas reseteadas exitosamente"}
