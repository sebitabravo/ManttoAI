"""Servicios de equipos con persistencia en base de datos."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipo import Equipo
from app.schemas.equipo import EquipoCreate, EquipoUpdate
from app.services.common import get_entity_or_404


def list_equipos(db: Session) -> list[Equipo]:
    """Lista equipos persistidos en la base de datos."""

    return list(db.scalars(select(Equipo).order_by(Equipo.id)))


def get_equipo_or_404(db: Session, equipo_id: int) -> Equipo:
    """Obtiene un equipo o retorna 404 cuando no existe."""

    return get_entity_or_404(db, Equipo, equipo_id, "Equipo no encontrado")


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
