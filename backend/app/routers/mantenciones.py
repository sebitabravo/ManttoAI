"""Endpoints de mantenciones."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.mantencion import (
    MantencionCreate,
    MantencionResponse,
    MantencionUpdate,
)
from app.services.mantencion_service import (
    create_mantencion,
    delete_mantencion,
    get_mantencion_or_404,
    list_mantenciones,
    update_mantencion,
)

router = APIRouter(prefix="/mantenciones", tags=["mantenciones"])


@router.get("", response_model=list[MantencionResponse])
def get_mantenciones(
    equipo_id: int | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=5000),
    order: Literal["asc", "desc"] = Query(default="asc"),
    db: Session = Depends(get_db),
) -> list[MantencionResponse]:
    """Lista mantenciones persistidas."""

    return list_mantenciones(db, equipo_id=equipo_id, limit=limit, order=order)


@router.get("/{mantencion_id}", response_model=MantencionResponse)
def get_mantencion_by_id(
    mantencion_id: int,
    db: Session = Depends(get_db),
) -> MantencionResponse:
    """Obtiene una mantención por identificador."""

    return get_mantencion_or_404(db, mantencion_id)


@router.post("", response_model=MantencionResponse, status_code=status.HTTP_201_CREATED)
def post_mantencion(
    payload: MantencionCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> MantencionResponse:
    """Crea una mantención persistida."""

    mantencion = create_mantencion(db, payload)
    response.headers["Location"] = str(
        request.url_for("get_mantencion_by_id", mantencion_id=str(mantencion.id))
    )
    return mantencion


@router.put("/{mantencion_id}", response_model=MantencionResponse)
def put_mantencion(
    mantencion_id: int,
    payload: MantencionUpdate,
    db: Session = Depends(get_db),
) -> MantencionResponse:
    """Actualiza una mantención persistida."""

    return update_mantencion(db, mantencion_id, payload)


@router.delete("/{mantencion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mantencion_by_id(
    mantencion_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Elimina una mantención por identificador."""

    delete_mantencion(db, mantencion_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
