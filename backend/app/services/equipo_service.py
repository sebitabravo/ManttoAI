"""Servicios de equipos con persistencia en base de datos."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipo import Equipo
from app.schemas.equipo import EquipoCreate, EquipoUpdate


def list_equipos(db: Session) -> list[Equipo]:
    """Lista equipos persistidos en la base de datos."""

    return list(db.scalars(select(Equipo).order_by(Equipo.id)))


def get_equipo_or_404(db: Session, equipo_id: int) -> Equipo:
    """Obtiene un equipo o retorna 404 cuando no existe."""

    equipo = db.get(Equipo, equipo_id)
    if equipo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado",
        )
    return equipo


def get_equipo(db: Session, equipo_id: int) -> Equipo:
    """Entrega un equipo por identificador."""

    return get_equipo_or_404(db, equipo_id)


def create_equipo(db: Session, payload: EquipoCreate) -> Equipo:
    """Crea y persiste un equipo."""

    equipo = Equipo(**payload.model_dump())
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return equipo


def update_equipo(db: Session, equipo_id: int, payload: EquipoUpdate) -> Equipo:
    """Actualiza un equipo existente en la base de datos."""

    equipo = get_equipo_or_404(db, equipo_id)
    cambios = payload.model_dump(exclude_unset=True)

    for key, value in cambios.items():
        setattr(equipo, key, value)

    db.commit()
    db.refresh(equipo)
    return equipo


def delete_equipo(db: Session, equipo_id: int) -> None:
    """Elimina un equipo existente en la base de datos."""

    equipo = get_equipo_or_404(db, equipo_id)
    db.delete(equipo)
    db.commit()
