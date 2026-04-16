"""Endpoints de alertas."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.middleware.rate_limit import limiter
from app.schemas.alerta import (
    AlertaCountResponse,
    AlertaMarkReadResponse,
    AlertaResponse,
)
from app.services.alerta_service import count_alertas, list_alertas, mark_as_read

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get(
    "",
    response_model=list[AlertaResponse],
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
def get_alertas(
    request: Request,
    equipo_id: int | None = Query(default=None),
    solo_no_leidas: bool = Query(default=False),
    limite: int | None = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[AlertaResponse]:
    """Lista alertas persistidas con filtros de consulta."""

    return list_alertas(
        db,
        equipo_id=equipo_id,
        solo_no_leidas=solo_no_leidas,
        limite=limite,
    )


@router.patch(
    "/{alerta_id}/leer",
    response_model=AlertaMarkReadResponse,
    dependencies=[Depends(require_role("admin", "tecnico"))],
)
def patch_alerta(
    alerta_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> AlertaMarkReadResponse:
    """Marca una alerta como leída."""

    return mark_as_read(db, alerta_id)


@router.get(
    "/count",
    response_model=AlertaCountResponse,
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
def get_alertas_count(
    request: Request,
    equipo_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> AlertaCountResponse:
    """Retorna conteo total y no leído de alertas."""

    counts = count_alertas(db, equipo_id=equipo_id)
    return AlertaCountResponse(**counts)
