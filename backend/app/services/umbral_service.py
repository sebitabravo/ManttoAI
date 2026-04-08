"""Servicios de umbrales con persistencia en base de datos."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.umbral import Umbral
from app.schemas.umbral import UmbralCreate, UmbralUpdate
from app.services.common import get_entity_or_404
from app.services.equipo_service import get_equipo_or_404


def _validate_umbral_limits(valor_min: float, valor_max: float) -> None:
    """Valida que los límites del umbral sean coherentes."""

    if valor_min > valor_max:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="valor_min no puede ser mayor que valor_max",
        )


def list_umbrales(db: Session, equipo_id: int | None = None) -> list[Umbral]:
    """Lista umbrales persistidos opcionalmente filtrando por equipo."""

    query = select(Umbral)
    if equipo_id is not None:
        query = query.where(Umbral.equipo_id == equipo_id)

    query = query.order_by(Umbral.equipo_id.asc(), Umbral.id.asc())
    return list(db.scalars(query))


def get_umbral_or_404(db: Session, umbral_id: int) -> Umbral:
    """Obtiene un umbral o retorna 404 cuando no existe."""

    return get_entity_or_404(db, Umbral, umbral_id, "Umbral no encontrado")


def create_umbral(db: Session, payload: UmbralCreate) -> Umbral:
    """Crea y persiste un umbral asociado a un equipo existente."""

    _validate_umbral_limits(payload.valor_min, payload.valor_max)
    get_equipo_or_404(db, payload.equipo_id)
    umbral = Umbral(**payload.model_dump())
    db.add(umbral)
    db.commit()
    db.refresh(umbral)
    return umbral


def update_umbral(db: Session, umbral_id: int, payload: UmbralUpdate) -> Umbral:
    """Actualiza un umbral existente en la base de datos."""

    umbral = get_umbral_or_404(db, umbral_id)
    cambios = payload.model_dump(exclude_unset=True)

    valor_min = cambios.get("valor_min", umbral.valor_min)
    valor_max = cambios.get("valor_max", umbral.valor_max)
    _validate_umbral_limits(valor_min, valor_max)

    for key, value in cambios.items():
        setattr(umbral, key, value)

    db.commit()
    db.refresh(umbral)
    return umbral


def delete_umbral(db: Session, umbral_id: int) -> None:
    """Elimina un umbral existente en la base de datos."""

    umbral = get_umbral_or_404(db, umbral_id)
    db.delete(umbral)
    db.commit()
