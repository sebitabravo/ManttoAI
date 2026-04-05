"""Endpoints de equipos."""

from fastapi import APIRouter

from app.schemas.equipo import EquipoCreate, EquipoResponse, EquipoUpdate
from app.services.equipo_service import (
    create_equipo,
    get_equipo,
    list_equipos,
    update_equipo,
)

router = APIRouter(prefix="/equipos", tags=["equipos"])


@router.get("", response_model=list[EquipoResponse])
def get_equipos() -> list[EquipoResponse]:
    """Lista equipos disponibles."""

    return list_equipos()


@router.get("/{equipo_id}", response_model=EquipoResponse)
def get_equipo_by_id(equipo_id: int) -> EquipoResponse:
    """Obtiene un equipo por identificador."""

    return get_equipo(equipo_id)


@router.post("", response_model=EquipoResponse)
def post_equipo(payload: EquipoCreate) -> EquipoResponse:
    """Crea un equipo demo."""

    return create_equipo(payload)


@router.put("/{equipo_id}", response_model=EquipoResponse)
def put_equipo(equipo_id: int, payload: EquipoUpdate) -> EquipoResponse:
    """Actualiza un equipo demo."""

    return update_equipo(equipo_id, payload)
