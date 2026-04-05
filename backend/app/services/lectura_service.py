"""Servicios de lecturas telemétricas con persistencia en base de datos."""

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lectura import Lectura
from app.schemas.lectura import LecturaCreate, LecturaMqttPayload
from app.services.alerta_service import (
    dispatch_critical_email_notifications,
    evaluate_thresholds,
)
from app.services.equipo_service import get_equipo_or_404

logger = logging.getLogger(__name__)


def list_lecturas(
    db: Session,
    equipo_id: int | None = None,
    limit: int | None = None,
) -> list[Lectura]:
    """Lista lecturas persistidas, opcionalmente filtradas por equipo."""

    query = select(Lectura)
    if equipo_id is not None:
        query = query.where(Lectura.equipo_id == equipo_id)

    query = query.order_by(Lectura.timestamp.desc(), Lectura.id.desc())
    if limit is not None:
        query = query.limit(limit)

    return list(db.scalars(query))


def get_latest_lectura(db: Session, equipo_id: int) -> Lectura:
    """Obtiene la última lectura persistida de un equipo."""

    lectura = db.scalars(
        select(Lectura)
        .where(Lectura.equipo_id == equipo_id)
        .order_by(Lectura.timestamp.desc(), Lectura.id.desc())
        .limit(1)
    ).first()

    if lectura is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lectura no encontrada para el equipo",
        )

    return lectura


def create_lectura(db: Session, payload: LecturaCreate) -> Lectura:
    """Crea y persiste una lectura asociada a un equipo existente."""

    get_equipo_or_404(db, payload.equipo_id)
    lectura = Lectura(**payload.model_dump(exclude_none=True))
    db.add(lectura)

    try:
        db.flush()
        alertas_creadas = evaluate_thresholds(db, lectura)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(lectura)
    try:
        dispatch_critical_email_notifications(db, alertas_creadas)
    except Exception:
        logger.exception(
            "No se pudo despachar notificación crítica para lectura id=%s",
            lectura.id,
        )

    return lectura


def create_lectura_from_mqtt_payload(
    db: Session,
    equipo_id: int,
    payload: LecturaMqttPayload,
) -> Lectura:
    """Persiste una lectura MQTT transformándola al schema de creación."""

    lectura_create = LecturaCreate(
        equipo_id=equipo_id,
        **payload.model_dump(exclude_none=True),
    )
    return create_lectura(db, lectura_create)
