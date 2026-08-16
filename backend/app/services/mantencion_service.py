"""Servicios de mantenciones con persistencia en base de datos."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipo import Equipo
from app.models.mantencion import Mantencion
from app.schemas.mantencion import MantencionCreate, MantencionUpdate
from app.services.equipo_service import get_equipo_or_404
from app.services.tenant_scope import (
    UNSCOPED,
    add_organization_scope,
    resolve_organization_id,
)


def list_mantenciones(
    db: Session,
    equipo_id: int | None = None,
    limit: int | None = None,
    order: str = "asc",
    organization_id: int | None | object = UNSCOPED,
) -> list[Mantencion]:
    """Lista mantenciones persistidas en la base de datos."""

    query = select(Mantencion).join(Equipo, Equipo.id == Mantencion.equipo_id)
    if equipo_id is not None:
        query = query.where(Mantencion.equipo_id == equipo_id)
    query = add_organization_scope(query, Equipo.organizacion_id, db, organization_id)

    if order == "asc":
        query = query.order_by(Mantencion.created_at.asc(), Mantencion.id.asc())
    else:
        query = query.order_by(Mantencion.created_at.desc(), Mantencion.id.desc())

    if limit is not None:
        query = query.limit(limit)

    return list(db.scalars(query))


def get_mantencion_or_404(
    db: Session, mantencion_id: int, organization_id: int | None | object = UNSCOPED
) -> Mantencion:
    """Obtiene una mantención o retorna 404 cuando no existe."""

    from fastapi import HTTPException, status

    query = add_organization_scope(
        select(Mantencion)
        .join(Equipo, Equipo.id == Mantencion.equipo_id)
        .where(Mantencion.id == mantencion_id),
        Equipo.organizacion_id,
        db,
        organization_id,
    )
    mantencion = db.scalars(query).first()
    if mantencion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mantención no encontrada",
        )
    return mantencion


def create_mantencion(
    db: Session,
    payload: MantencionCreate,
    organization_id: int | None | object = UNSCOPED,
) -> Mantencion:
    """Crea y persiste una mantención asociada a un equipo existente."""

    equipo = get_equipo_or_404(db, payload.equipo_id, organization_id)
    values = payload.model_dump()
    resolved_id = resolve_organization_id(db, organization_id)
    if resolved_id is UNSCOPED:
        resolved_id = equipo.organizacion_id
    if resolved_id is not UNSCOPED:
        values["organizacion_id"] = resolved_id
    mantencion = Mantencion(**values)
    db.add(mantencion)
    db.commit()
    db.refresh(mantencion)
    return mantencion


def update_mantencion(
    db: Session,
    mantencion_id: int,
    payload: MantencionUpdate,
    organization_id: int | None | object = UNSCOPED,
) -> Mantencion:
    """Actualiza una mantención existente en la base de datos."""

    mantencion = get_mantencion_or_404(db, mantencion_id, organization_id)
    cambios = payload.model_dump(exclude_unset=True)

    for key, value in cambios.items():
        setattr(mantencion, key, value)

    db.commit()
    db.refresh(mantencion)
    return mantencion


def delete_mantencion(
    db: Session, mantencion_id: int, organization_id: int | None | object = UNSCOPED
) -> None:
    """Elimina una mantención existente en la base de datos."""

    mantencion = get_mantencion_or_404(db, mantencion_id, organization_id)
    db.delete(mantencion)
    db.commit()
