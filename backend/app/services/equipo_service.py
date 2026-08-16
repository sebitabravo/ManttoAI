"""Servicios de equipos con persistencia en base de datos."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.equipo import Equipo
from app.models.umbral import Umbral
from app.schemas.equipo import EquipoCreate, EquipoFullSetupRequest, EquipoUpdate
from app.services.tenant_scope import (
    UNSCOPED,
    add_organization_scope,
    resolve_organization_id,
)


def list_equipos(
    db: Session, organization_id: int | None | object = UNSCOPED
) -> list[Equipo]:
    """Lista equipos persistidos en la base de datos."""

    query = add_organization_scope(
        select(Equipo), Equipo.organizacion_id, db, organization_id
    ).order_by(Equipo.id)
    return list(db.scalars(query))


def get_equipo_or_404(
    db: Session, equipo_id: int, organization_id: int | None | object = UNSCOPED
) -> Equipo:
    """Obtiene un equipo o retorna 404 cuando no existe."""

    from fastapi import HTTPException, status

    query = add_organization_scope(
        select(Equipo).where(Equipo.id == equipo_id),
        Equipo.organizacion_id,
        db,
        organization_id,
    )
    equipo = db.scalars(query).first()
    if equipo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado"
        )
    return equipo


def create_equipo(
    db: Session,
    payload: EquipoCreate,
    organization_id: int | None | object = UNSCOPED,
    commit: bool = True,
) -> Equipo:
    """Crea y persiste un equipo, opcionalmente dentro de una transacción."""

    values = payload.model_dump()
    resolved_id = resolve_organization_id(db, organization_id)
    if resolved_id is not UNSCOPED:
        values["organizacion_id"] = resolved_id
    equipo = Equipo(**values)
    db.add(equipo)
    if commit:
        db.commit()
        db.refresh(equipo)
    else:
        db.flush()
    return equipo


def create_equipo_with_umbrales(
    db: Session,
    payload: EquipoFullSetupRequest,
    organization_id: int | None | object = UNSCOPED,
) -> tuple[Equipo, Umbral, Umbral]:
    """Crea un equipo y sus umbrales en una transacción atómica."""

    resolved_id = resolve_organization_id(db, organization_id)
    values = {
        "nombre": payload.nombre,
        "ubicacion": payload.ubicacion or "Laboratorio",
        "tipo": payload.tipo or "Motor",
        "rubro": payload.rubro,
        "descripcion": payload.descripcion or "Equipo monitoreado por ManttoAI",
        "estado": "operativo",
        "mac_address": payload.mac_address,
    }
    if resolved_id is not UNSCOPED:
        values["organizacion_id"] = resolved_id

    equipo = Equipo(**values)
    db.add(equipo)

    try:
        db.flush()

        umbral_temp = Umbral(
            equipo_id=equipo.id,
            variable="temperatura",
            valor_min=0,
            valor_max=payload.temperatura_max,
            organizacion_id=(None if resolved_id is UNSCOPED else resolved_id),
        )
        umbral_vib = Umbral(
            equipo_id=equipo.id,
            variable="vibracion",
            valor_min=0,
            valor_max=payload.vibracion_max,
            organizacion_id=(None if resolved_id is UNSCOPED else resolved_id),
        )
        db.add_all([umbral_temp, umbral_vib])
        db.flush()
        db.commit()
    except Exception:
        db.rollback()
        raise

    return equipo, umbral_temp, umbral_vib


def update_equipo(
    db: Session,
    equipo_id: int,
    payload: EquipoUpdate,
    organization_id: int | None | object = UNSCOPED,
) -> Equipo:
    """Actualiza un equipo existente en la base de datos."""

    equipo = get_equipo_or_404(db, equipo_id, organization_id)
    cambios = payload.model_dump(exclude_unset=True)

    for key, value in cambios.items():
        setattr(equipo, key, value)

    db.commit()
    db.refresh(equipo)
    return equipo


def delete_equipo(
    db: Session, equipo_id: int, organization_id: int | None | object = UNSCOPED
) -> None:
    """Elimina un equipo existente en la base de datos."""

    equipo = get_equipo_or_404(db, equipo_id, organization_id)
    db.delete(equipo)
    db.commit()
