"""Servicios de lecturas telemétricas con persistencia en base de datos."""

import logging
from collections.abc import Callable
from smtplib import SMTPException

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.lectura import Lectura
from app.schemas.lectura import LecturaCreate, LecturaMqttPayload
from app.services.alerta_service import (
    dispatch_critical_email_notifications,
    dispatch_critical_email_notifications_bg,
    evaluate_thresholds,
)
from app.services.equipo_service import get_equipo_or_404

logger = logging.getLogger(__name__)


def list_lecturas(
    db: Session,
    equipo_id: int | None = None,
    limit: int | None = 100,
    offset: int | None = None,
) -> list[Lectura]:
    """Lista lecturas persistidas con orden descendente, límite y offset opcionales."""

    query = select(Lectura)
    if equipo_id is not None:
        query = query.where(Lectura.equipo_id == equipo_id)

    query = query.order_by(Lectura.timestamp.desc(), Lectura.id.desc())
    if offset is not None:
        query = query.offset(offset)
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


def create_lectura(
    db: Session,
    payload: LecturaCreate,
    background_tasks: BackgroundTasks | None = None,
    session_factory: Callable | None = None,
) -> Lectura:
    """Crea y persiste una lectura asociada a un equipo existente."""

    get_equipo_or_404(db, payload.equipo_id)
    lectura = Lectura(**payload.model_dump(exclude_none=True))
    db.add(lectura)

    try:
        db.flush()
        alertas_creadas = evaluate_thresholds(db, lectura)
        db.commit()
    except IntegrityError:
        # Race condition: otra lectura concurrente ya creó la misma alerta.
        # Revertimos y persistimos solo la lectura para no perder datos.
        db.rollback()
        db.add(lectura)
        db.flush()
        # Re-evaluar sin crear duplicados: verificar alertas existentes
        from app.models.alerta import Alerta
        from app.models.umbral import Umbral
        from app.services.alerta_service import (
            _is_out_of_range,
            _resolve_alert_type,
            _resolve_threshold_target,
        )

        alertas_creadas = []
        umbrales = list(
            db.scalars(select(Umbral).where(Umbral.equipo_id == lectura.equipo_id))
        )
        for umbral in umbrales:
            target = _resolve_threshold_target(lectura, umbral.variable)
            if target is None:
                continue
            valor, mensaje_alerta = target
            if not _is_out_of_range(valor, umbral.valor_min, umbral.valor_max):
                continue
            tipo_alerta = _resolve_alert_type(umbral.variable)
            # Verificar si ya existe cualquier alerta con esta clave
            existente = db.scalars(
                select(Alerta)
                .where(Alerta.equipo_id == lectura.equipo_id)
                .where(Alerta.tipo == tipo_alerta)
                .where(Alerta.mensaje == mensaje_alerta)
                .where(Alerta.leida.is_(False))
                .limit(1)
            ).first()
            if existente is None:
                alerta = Alerta(
                    equipo_id=lectura.equipo_id,
                    tipo=tipo_alerta,
                    mensaje=mensaje_alerta,
                    nivel="alto",
                    email_enviado=False,
                    leida=False,
                )
                db.add(alerta)
                alertas_creadas.append(alerta)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(lectura)

    if not alertas_creadas:
        return lectura

    alerta_ids = [a.id for a in alertas_creadas if a.nivel == "alto"]
    if not alerta_ids:
        return lectura

    if background_tasks:
        background_tasks.add_task(
            dispatch_critical_email_notifications_bg,
            alerta_ids,
            session_factory,
        )
    else:
        try:
            dispatch_critical_email_notifications(db, alertas_creadas)
        except (SQLAlchemyError, RuntimeError, OSError, SMTPException):
            logger.exception(
                "No se pudo despachar notificación crítica para lectura id=%s",
                lectura.id,
            )

    return lectura


def create_lectura_from_mqtt_payload(
    db: Session,
    equipo_id: int,
    payload: LecturaMqttPayload,
    background_tasks: BackgroundTasks | None = None,
    session_factory: Callable | None = None,
) -> Lectura:
    """Persiste una lectura MQTT transformándola al schema de creación."""

    lectura_create = LecturaCreate(
        equipo_id=equipo_id,
        **payload.model_dump(exclude_none=True),
    )
    return create_lectura(
        db,
        lectura_create,
        background_tasks=background_tasks,
        session_factory=session_factory,
    )
