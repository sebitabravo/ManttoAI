"""Endpoints de equipos."""

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.equipo import EquipoCreate, EquipoResponse, EquipoUpdate
from app.services.equipo_service import (
    create_equipo,
    delete_equipo,
    get_equipo_or_404,
    list_equipos,
    update_equipo,
)

router = APIRouter(prefix="/equipos", tags=["equipos"])


@router.get("", response_model=list[EquipoResponse])
def get_equipos(db: Session = Depends(get_db)) -> list[EquipoResponse]:
    """Lista equipos disponibles."""

    return list_equipos(db)


@router.get("/{equipo_id}", response_model=EquipoResponse)
def get_equipo_by_id(equipo_id: int, db: Session = Depends(get_db)) -> EquipoResponse:
    """Obtiene un equipo por identificador."""

    return get_equipo_or_404(db, equipo_id)


@router.post("", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
def post_equipo(
    payload: EquipoCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> EquipoResponse:
    """Crea un equipo persistido."""

    equipo = create_equipo(db, payload)
    response.headers["Location"] = str(
        request.url_for("get_equipo_by_id", equipo_id=str(equipo.id))
    )
    return equipo


@router.put("/{equipo_id}", response_model=EquipoResponse)
def put_equipo(
    equipo_id: int, payload: EquipoUpdate, db: Session = Depends(get_db)
) -> EquipoResponse:
    """Actualiza un equipo persistido."""

    return update_equipo(db, equipo_id, payload)


@router.delete("/{equipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipo_by_id(equipo_id: int, db: Session = Depends(get_db)) -> Response:
    """Elimina un equipo por identificador."""

    delete_equipo(db, equipo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
