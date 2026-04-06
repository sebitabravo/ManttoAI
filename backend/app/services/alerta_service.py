"""Servicios de alertas y evaluación básica de umbrales."""

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.umbral import Umbral
from app.services.common import get_entity_or_404
from app.services.email_service import send_alert_email

PREDICTION_ALERT_TYPE = "prediccion"
logger = logging.getLogger(__name__)


def _is_out_of_range(value: float, valor_min: float, valor_max: float) -> bool:
    """Indica si un valor está fuera del rango definido por umbral."""

    return value < valor_min or value > valor_max


def _resolve_threshold_target(
    lectura: Lectura, variable: str
) -> tuple[float, str] | None:
    """Mapea variable de umbral al valor de lectura y metadata de alerta."""

    variable_key = variable.lower().strip()

    if variable_key == "temperatura":
        return lectura.temperatura, "Temperatura fuera de rango"

    if variable_key == "vibracion":
        valor_vibracion = max(
            abs(lectura.vib_x), abs(lectura.vib_y), abs(lectura.vib_z)
        )
        return valor_vibracion, "Vibración fuera de rango"

    if variable_key in {"vib_x", "vib_y", "vib_z"}:
        return (
            getattr(lectura, variable_key),
            f"Vibración {variable_key} fuera de rango",
        )

    return None


def evaluate_thresholds(db: Session, lectura: Lectura) -> list[Alerta]:
    """Evalúa umbrales y agrega alertas en sesión; el caller realiza commit."""

    umbrales = list(
        db.scalars(select(Umbral).where(Umbral.equipo_id == lectura.equipo_id))
    )
    alertas_creadas: list[Alerta] = []

    for umbral in umbrales:
        if umbral.valor_min > umbral.valor_max:
            continue

        target = _resolve_threshold_target(lectura, umbral.variable)
        if target is None:
            continue

        valor_medido, mensaje_alerta = target
        if not _is_out_of_range(valor_medido, umbral.valor_min, umbral.valor_max):
            continue

        tipo_alerta = (
            "temperatura"
            if umbral.variable.lower().strip() == "temperatura"
            else "vibracion"
        )
        alerta_activa = db.scalars(
            select(Alerta)
            .where(Alerta.equipo_id == lectura.equipo_id)
            .where(Alerta.tipo == tipo_alerta)
            .where(Alerta.mensaje == mensaje_alerta)
            .where(Alerta.leida.is_(False))
            .limit(1)
        ).first()
        if alerta_activa is not None:
            continue

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

    return alertas_creadas


def list_alertas(
    db: Session,
    equipo_id: int | None = None,
    solo_no_leidas: bool = False,
    limite: int | None = 50,
) -> list[Alerta]:
    """Lista alertas persistidas con filtros simples de consulta."""

    query = select(Alerta)
    if equipo_id is not None:
        query = query.where(Alerta.equipo_id == equipo_id)
    if solo_no_leidas:
        query = query.where(Alerta.leida.is_(False))

    query = query.order_by(Alerta.created_at.desc(), Alerta.id.desc())
    if limite is not None:
        query = query.limit(limite)

    return list(db.scalars(query))


def get_active_prediction_failure_alert(db: Session, equipo_id: int) -> Alerta | None:
    """Obtiene alerta activa de predicción para un equipo, si existe."""

    return db.scalars(
        select(Alerta)
        .where(Alerta.equipo_id == equipo_id)
        .where(Alerta.tipo == PREDICTION_ALERT_TYPE)
        .where(Alerta.nivel == "alto")
        .where(Alerta.leida.is_(False))
        .limit(1)
    ).first()


def _lock_equipo_alert_scope(db: Session, equipo_id: int) -> None:
    """Bloquea fila del equipo para deduplicar alertas concurrentes cuando el motor lo soporta."""

    try:
        db.execute(
            select(Equipo.id).where(Equipo.id == equipo_id).with_for_update()
        ).first()
    except (OperationalError, DBAPIError) as exc:
        logger.debug(
            "FOR UPDATE no soportado por el motor actual; se usará fallback por constraint. detalle=%s",
            exc,
        )


def get_alerta_or_404(db: Session, alerta_id: int) -> Alerta:
    """Obtiene una alerta por id o retorna 404 si no existe."""

    return get_entity_or_404(db, Alerta, alerta_id, "Alerta no encontrada")


def mark_as_read(db: Session, alerta_id: int) -> dict[str, int | bool]:
    """Marca una alerta persistida como leída."""

    alerta = get_alerta_or_404(db, alerta_id)
    alerta.leida = True
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(alerta)
    return {"id": alerta.id, "leida": alerta.leida}


def dispatch_critical_email_notifications(db: Session, alertas: list[Alerta]) -> None:
    """Intenta enviar email para alertas críticas ya persistidas."""

    if not alertas:
        return

    for alerta in alertas:
        if alerta.nivel != "alto":
            continue

        try:
            email_result = send_alert_email(
                "Alerta crítica ManttoAI",
                (
                    f"Equipo {alerta.equipo_id}: {alerta.mensaje}. "
                    f"Tipo de alerta: {alerta.tipo}."
                ),
            )
        except Exception as exc:  # pragma: no cover - defensa ante mocks/integraciones
            logger.warning(
                "No se pudo invocar envío de email para alerta crítica alerta_id=%s error=%s",
                getattr(alerta, "id", None),
                exc,
            )
            alerta.email_enviado = False
            continue

        sent = False
        if isinstance(email_result, dict):
            sent = bool(email_result.get("sent"))
            if email_result.get("error"):
                logger.warning(
                    "No se pudo enviar email de alerta crítica alerta_id=%s error=%s",
                    getattr(alerta, "id", None),
                    email_result.get("error"),
                )
        alerta.email_enviado = sent

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("No se pudo persistir estado de emails de alertas")
        raise


def create_prediction_failure_alert(
    db: Session,
    equipo_id: int,
    probabilidad: float,
    auto_commit: bool = True,
) -> Alerta | None:
    """Crea alerta crítica por predicción de falla evitando duplicados activos."""

    _lock_equipo_alert_scope(db, equipo_id)
    alerta_activa = get_active_prediction_failure_alert(db, equipo_id)

    if alerta_activa is not None:
        return None

    alerta = Alerta(
        equipo_id=equipo_id,
        tipo=PREDICTION_ALERT_TYPE,
        mensaje=(
            "Predicción de falla detectada por modelo ML. "
            f"Probabilidad estimada: {probabilidad:.2f}"
        ),
        nivel="alto",
        email_enviado=False,
        leida=False,
    )
    db.add(alerta)

    if not auto_commit:
        return alerta

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return get_active_prediction_failure_alert(db, equipo_id)
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(alerta)
    dispatch_critical_email_notifications(db, [alerta])
    return alerta
