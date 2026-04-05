"""Endpoints de lecturas."""

from fastapi import APIRouter, Query

from app.schemas.lectura import LecturaCreate, LecturaResponse
from app.services.lectura_service import (
    create_lectura,
    get_latest_lectura,
    list_lecturas,
)

router = APIRouter(prefix="/lecturas", tags=["lecturas"])


@router.get("", response_model=list[LecturaResponse])
def get_lecturas(equipo_id: int | None = Query(default=None)) -> list[LecturaResponse]:
    """Entrega historial demo de lecturas."""

    return list_lecturas(equipo_id)


@router.get("/latest/{equipo_id}", response_model=LecturaResponse)
def get_latest(equipo_id: int) -> LecturaResponse:
    """Entrega la última lectura demo de un equipo."""

    return get_latest_lectura(equipo_id)


@router.post("", response_model=LecturaResponse)
def post_lectura(payload: LecturaCreate) -> LecturaResponse:
    """Crea una lectura demo."""

    return create_lectura(payload)
