"""Endpoints de umbrales."""

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.umbral import UmbralCreate, UmbralResponse, UmbralUpdate
from app.services.umbral_service import (
    create_umbral,
    delete_umbral,
    get_umbral_or_404,
    list_umbrales,
    update_umbral,
)

router = APIRouter(prefix="/umbrales", tags=["umbrales"])


@router.get("", response_model=list[UmbralResponse])
def get_umbrales(
    equipo_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[UmbralResponse]:
    """Lista umbrales persistidos con filtro opcional por equipo."""

    return list_umbrales(db, equipo_id=equipo_id)


@router.get("/equipo/{equipo_id}", response_model=list[UmbralResponse])
def get_umbrales_by_equipo(
    equipo_id: int,
    db: Session = Depends(get_db),
) -> list[UmbralResponse]:
    """Lista umbrales asociados a un equipo específico."""

    return list_umbrales(db, equipo_id=equipo_id)


@router.get("/{umbral_id}", response_model=UmbralResponse)
def get_umbral_by_id(
    umbral_id: int,
    db: Session = Depends(get_db),
) -> UmbralResponse:
    """Obtiene un umbral por identificador."""

    return get_umbral_or_404(db, umbral_id)


@router.post("", response_model=UmbralResponse, status_code=status.HTTP_201_CREATED)
def post_umbral(
    payload: UmbralCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> UmbralResponse:
    """Crea un umbral persistido."""

    umbral = create_umbral(db, payload)
    response.headers["Location"] = str(
        request.url_for("get_umbral_by_id", umbral_id=str(umbral.id))
    )
    return umbral


@router.post(
    "/equipo/{equipo_id}",
    response_model=UmbralResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_umbral_by_equipo(
    equipo_id: int,
    payload: UmbralCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> UmbralResponse:
    """Crea un umbral asegurando asociación al equipo de la ruta."""

    normalized_payload = payload.model_copy(update={"equipo_id": equipo_id})
    umbral = create_umbral(db, normalized_payload)
    response.headers["Location"] = str(
        request.url_for("get_umbral_by_id", umbral_id=str(umbral.id))
    )
    return umbral


@router.put("/{umbral_id}", response_model=UmbralResponse)
def put_umbral(
    umbral_id: int,
    payload: UmbralUpdate,
    db: Session = Depends(get_db),
) -> UmbralResponse:
    """Actualiza un umbral persistido."""

    return update_umbral(db, umbral_id, payload)


@router.delete("/{umbral_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_umbral_by_id(umbral_id: int, db: Session = Depends(get_db)) -> Response:
    """Elimina un umbral por identificador."""

    delete_umbral(db, umbral_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
