"""Servicios de umbrales con persistencia en base de datos."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipo import Equipo
from app.models.umbral import Umbral
from app.schemas.umbral import UmbralCreate, UmbralUpdate
from app.services.equipo_service import get_equipo_or_404
from app.services.tenant_scope import (
    UNSCOPED,
    add_organization_scope,
    resolve_organization_id,
)


def _validate_umbral_limits(valor_min: float, valor_max: float) -> None:
    """Valida que los límites del umbral sean coherentes."""

    if valor_min > valor_max:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="valor_min no puede ser mayor que valor_max",
        )


def list_umbrales(
    db: Session,
    equipo_id: int | None = None,
    organization_id: int | None | object = UNSCOPED,
) -> list[Umbral]:
    """Lista umbrales persistidos opcionalmente filtrando por equipo."""

    query = select(Umbral).join(Equipo, Equipo.id == Umbral.equipo_id)
    if equipo_id is not None:
        query = query.where(Umbral.equipo_id == equipo_id)
    query = add_organization_scope(query, Equipo.organizacion_id, db, organization_id)

    query = query.order_by(Umbral.equipo_id.asc(), Umbral.id.asc())
    return list(db.scalars(query))


def get_umbral_or_404(
    db: Session, umbral_id: int, organization_id: int | None | object = UNSCOPED
) -> Umbral:
    """Obtiene un umbral o retorna 404 cuando no existe."""

    from fastapi import HTTPException

    query = add_organization_scope(
        select(Umbral)
        .join(Equipo, Equipo.id == Umbral.equipo_id)
        .where(Umbral.id == umbral_id),
        Equipo.organizacion_id,
        db,
        organization_id,
    )
    umbral = db.scalars(query).first()
    if umbral is None:
        raise HTTPException(status_code=404, detail="Umbral no encontrado")
    return umbral


def create_umbral(
    db: Session,
    payload: UmbralCreate,
    organization_id: int | None | object = UNSCOPED,
) -> Umbral:
    """Crea y persiste un umbral asociado a un equipo existente."""

    _validate_umbral_limits(payload.valor_min, payload.valor_max)
    equipo = get_equipo_or_404(db, payload.equipo_id, organization_id)
    values = payload.model_dump()
    resolved_id = resolve_organization_id(db, organization_id)
    if resolved_id is UNSCOPED:
        resolved_id = equipo.organizacion_id
    if resolved_id is not UNSCOPED:
        values["organizacion_id"] = resolved_id
    umbral = Umbral(**values)
    db.add(umbral)
    db.commit()
    db.refresh(umbral)
    return umbral


def update_umbral(
    db: Session,
    umbral_id: int,
    payload: UmbralUpdate,
    organization_id: int | None | object = UNSCOPED,
) -> Umbral:
    """Actualiza un umbral existente en la base de datos."""

    umbral = get_umbral_or_404(db, umbral_id, organization_id)
    cambios = payload.model_dump(exclude_unset=True)

    valor_min = cambios.get("valor_min", umbral.valor_min)
    valor_max = cambios.get("valor_max", umbral.valor_max)
    _validate_umbral_limits(valor_min, valor_max)

    for key, value in cambios.items():
        setattr(umbral, key, value)

    db.commit()
    db.refresh(umbral)
    return umbral


def delete_umbral(
    db: Session, umbral_id: int, organization_id: int | None | object = UNSCOPED
) -> None:
    """Elimina un umbral existente en la base de datos."""

    umbral = get_umbral_or_404(db, umbral_id, organization_id)
    db.delete(umbral)
    db.commit()
