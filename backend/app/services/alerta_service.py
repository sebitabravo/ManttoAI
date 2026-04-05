"""Servicios de alertas y evaluación básica de umbrales."""

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.models.lectura import Lectura
from app.models.umbral import Umbral
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


def get_alerta_or_404(db: Session, alerta_id: int) -> Alerta:
    """Obtiene una alerta por id o retorna 404 si no existe."""

    alerta = db.get(Alerta, alerta_id)
    if alerta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada",
        )
    return alerta


def mark_as_read(db: Session, alerta_id: int) -> dict[str, int | bool]:
    """Marca una alerta persistida como leída."""

    alerta = get_alerta_or_404(db, alerta_id)
    alerta.leida = True
    try:
        db.commit()
    except Exception:
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
                subject="Alerta crítica ManttoAI",
                message=(
                    f"Equipo {alerta.equipo_id}: {alerta.mensaje}. "
                    f"Tipo de alerta: {alerta.tipo}."
                ),
            )

            sent = False
            if isinstance(email_result, dict):
                sent = bool(email_result.get("sent"))
            alerta.email_enviado = sent
        except Exception:
            logger.exception(
                "No se pudo enviar email de alerta crítica (alerta_id=%s)",
                getattr(alerta, "id", None),
            )
            alerta.email_enviado = False

    try:
        db.commit()
    except Exception:
        db.rollback()


def create_prediction_failure_alert(
    db: Session,
    equipo_id: int,
    probabilidad: float,
) -> Alerta | None:
    """Crea alerta crítica por predicción de falla evitando duplicados activos."""

    alerta_activa = db.scalars(
        select(Alerta)
        .where(Alerta.equipo_id == equipo_id)
        .where(Alerta.tipo == PREDICTION_ALERT_TYPE)
        .where(Alerta.nivel == "alto")
        .where(Alerta.leida.is_(False))
        .limit(1)
    ).first()

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

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(alerta)
    dispatch_critical_email_notifications(db, [alerta])
    return alerta
