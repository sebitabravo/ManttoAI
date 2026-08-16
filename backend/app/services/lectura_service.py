"""Servicios de lecturas telemétricas con persistencia en base de datos."""

import logging
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from smtplib import SMTPException

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.schemas.lectura import LecturaCreate, LecturaMqttPayload
from app.services.alerta_service import (
    dispatch_critical_email_notifications,
    dispatch_critical_email_notifications_bg,
    evaluate_thresholds,
)
from app.services.equipo_service import get_equipo_or_404
from app.services.tenant_scope import (
    UNSCOPED,
    add_organization_scope,
    resolve_organization_id,
)

logger = logging.getLogger(__name__)


def list_lecturas(
    db: Session,
    equipo_id: int | None = None,
    limit: int | None = 100,
    offset: int | None = None,
    organization_id: int | None | object = UNSCOPED,
) -> list[Lectura]:
    """Lista lecturas persistidas con orden descendente, límite y offset opcionales."""

    query = select(Lectura).join(Equipo, Equipo.id == Lectura.equipo_id)
    if equipo_id is not None:
        query = query.where(Lectura.equipo_id == equipo_id)
    query = add_organization_scope(query, Equipo.organizacion_id, db, organization_id)

    query = query.order_by(Lectura.timestamp.desc(), Lectura.id.desc())
    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    return list(db.scalars(query))


def prune_old_lecturas(
    db: Session,
    retention_days: int,
    now: datetime | None = None,
) -> int:
    """Elimina lecturas anteriores a la ventana de retención configurada."""

    if retention_days <= 0:
        return 0

    reference_time = now or datetime.now(timezone.utc)
    cutoff = reference_time - timedelta(days=retention_days)
    try:
        result = db.execute(delete(Lectura).where(Lectura.timestamp < cutoff))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return int(result.rowcount or 0)


def get_latest_lectura(
    db: Session, equipo_id: int, organization_id: int | None | object = UNSCOPED
) -> Lectura:
    """Obtiene la última lectura persistida de un equipo."""

    query = (
        select(Lectura)
        .join(Equipo, Equipo.id == Lectura.equipo_id)
        .where(Lectura.equipo_id == equipo_id)
        .order_by(Lectura.timestamp.desc(), Lectura.id.desc())
        .limit(1)
    )
    lectura = db.scalars(
        add_organization_scope(query, Equipo.organizacion_id, db, organization_id)
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
    organization_id: int | None | object = UNSCOPED,
) -> Lectura:
    """Crea y persiste una lectura asociada a un equipo existente."""

    equipo = get_equipo_or_404(db, payload.equipo_id, organization_id)
    values = payload.model_dump(exclude_none=True)
    resolved_id = resolve_organization_id(db, organization_id)
    if resolved_id is UNSCOPED:
        resolved_id = equipo.organizacion_id
    if resolved_id is not UNSCOPED:
        values["organizacion_id"] = resolved_id
    lectura = Lectura(**values)
    db.add(lectura)

    try:
        db.flush()
        if resolved_id is None:
            # Mantiene compatibilidad con workers/tests que operan sobre equipos globales.
            alertas_creadas = evaluate_thresholds(db, lectura)
        else:
            alertas_creadas = evaluate_thresholds(db, lectura, resolved_id)
        db.flush()
        alerta_ids = [a.id for a in alertas_creadas if a.nivel == "alto"]
        db.commit()
    except IntegrityError:
        # Race condition: otra lectura concurrente ya creó la misma alerta.
        # Revertimos y persistimos solo la lectura para no perder datos.
        db.rollback()
        db.add(lectura)
        db.flush()
        # Re-evaluar usando la misma regla pública; el evaluador ya evita
        # alertas activas equivalentes bajo el lock del equipo.
        if resolved_id is None:
            alertas_creadas = evaluate_thresholds(db, lectura)
        else:
            alertas_creadas = evaluate_thresholds(db, lectura, resolved_id)
        db.flush()
        alerta_ids = [a.id for a in alertas_creadas if a.nivel == "alto"]
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(lectura)

    if not alertas_creadas:
        return lectura

    if not alerta_ids:
        return lectura

    if background_tasks:
        background_tasks.add_task(
            dispatch_critical_email_notifications_bg,
            alerta_ids,
            session_factory,
            run_inline=session_factory is not None,
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
    organization_id: int | None | object = UNSCOPED,
) -> Lectura:
    """Persiste una lectura MQTT transformándola al schema de creación."""

    lectura_create = LecturaCreate(
        equipo_id=equipo_id,
        **payload.model_dump(exclude_none=True),
    )
    kwargs = {
        "background_tasks": background_tasks,
        "session_factory": session_factory,
    }
    if organization_id is not UNSCOPED:
        kwargs["organization_id"] = organization_id
    return create_lectura(db, lectura_create, **kwargs)
