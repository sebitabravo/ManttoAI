"""Endpoints de lecturas."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.lectura import LecturaCreate, LecturaResponse
from app.services.lectura_service import (
    create_lectura,
    get_latest_lectura,
    list_lecturas,
)

router = APIRouter(prefix="/lecturas", tags=["lecturas"])


@router.get("", response_model=list[LecturaResponse])
def get_lecturas(
    equipo_id: int | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> list[LecturaResponse]:
    """Entrega historial persistido de lecturas con límite por defecto."""

    return list_lecturas(db, equipo_id, limit)


@router.get("/latest/{equipo_id}", response_model=LecturaResponse)
def get_latest(equipo_id: int, db: Session = Depends(get_db)) -> LecturaResponse:
    """Entrega la última lectura persistida de un equipo."""

    return get_latest_lectura(db, equipo_id)


@router.post("", response_model=LecturaResponse, status_code=status.HTTP_201_CREATED)
def post_lectura(
    payload: LecturaCreate,
    db: Session = Depends(get_db),
) -> LecturaResponse:
    """Crea una lectura persistida."""

    return create_lectura(db, payload)
