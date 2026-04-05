"""Endpoints de alertas."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.alerta import AlertaMarkReadResponse, AlertaResponse
from app.services.alerta_service import list_alertas, mark_as_read

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("", response_model=list[AlertaResponse])
def get_alertas(
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


@router.patch("/{alerta_id}/leer", response_model=AlertaMarkReadResponse)
def patch_alerta(
    alerta_id: int,
    db: Session = Depends(get_db),
) -> AlertaMarkReadResponse:
    """Marca una alerta como leída."""

    return mark_as_read(db, alerta_id)
