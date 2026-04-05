"""Servicios de mantenciones con persistencia en base de datos."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mantencion import Mantencion
from app.schemas.mantencion import MantencionCreate, MantencionUpdate
from app.services.equipo_service import get_equipo_or_404


def list_mantenciones(db: Session) -> list[Mantencion]:
    """Lista mantenciones persistidas en la base de datos."""

    return list(db.scalars(select(Mantencion).order_by(Mantencion.id)))


def get_mantencion_or_404(db: Session, mantencion_id: int) -> Mantencion:
    """Obtiene una mantención o retorna 404 cuando no existe."""

    mantencion = db.get(Mantencion, mantencion_id)
    if mantencion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mantención no encontrada",
        )
    return mantencion


def create_mantencion(db: Session, payload: MantencionCreate) -> Mantencion:
    """Crea y persiste una mantención asociada a un equipo existente."""

    get_equipo_or_404(db, payload.equipo_id)
    mantencion = Mantencion(**payload.model_dump())
    db.add(mantencion)
    db.commit()
    db.refresh(mantencion)
    return mantencion


def update_mantencion(
    db: Session, mantencion_id: int, payload: MantencionUpdate
) -> Mantencion:
    """Actualiza una mantención existente en la base de datos."""

    mantencion = get_mantencion_or_404(db, mantencion_id)
    cambios = payload.model_dump(exclude_unset=True)

    for key, value in cambios.items():
        setattr(mantencion, key, value)

    db.commit()
    db.refresh(mantencion)
    return mantencion


def delete_mantencion(db: Session, mantencion_id: int) -> None:
    """Elimina una mantención existente en la base de datos."""

    mantencion = get_mantencion_or_404(db, mantencion_id)
    db.delete(mantencion)
    db.commit()
