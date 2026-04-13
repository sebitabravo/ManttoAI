"""Servicios de alertas y evaluación básica de umbrales."""

import logging
from smtplib import SMTPException
import threading

from collections.abc import Callable
from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.umbral import Umbral
from app.database import SessionLocal
from app.services.common import get_entity_or_404
from app.services.email_service import (
    get_smtp_client,
    send_alert_email_with_client,
)

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

    if variable_key == "humedad":
        return lectura.humedad, "Humedad fuera de rango"

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


def _resolve_alert_type(variable: str) -> str:
    """Normaliza el tipo de alerta persistido para una variable monitoreada."""

    variable_normalizada = variable.lower().strip()
    if variable_normalizada == "temperatura":
        return "temperatura"
    if variable_normalizada == "humedad":
        return "humedad"
    return "vibracion"


def evaluate_thresholds(db: Session, lectura: Lectura) -> list[Alerta]:
    """Evalúa umbrales y agrega alertas en sesión; el caller realiza commit."""

    _lock_equipo_alert_scope(db, lectura.equipo_id)
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

        tipo_alerta = _resolve_alert_type(umbral.variable)
        # Evitar duplicados solo mientras exista una alerta activa equivalente.
        # Si la alerta anterior ya fue leída, una nueva anomalía debe generar
        # un nuevo registro para mantener trazabilidad del incidente.
        alerta_existente = db.scalars(
            select(Alerta)
            .where(Alerta.equipo_id == lectura.equipo_id)
            .where(Alerta.tipo == tipo_alerta)
            .where(Alerta.mensaje == mensaje_alerta)
            .where(Alerta.leida.is_(False))
            .limit(1)
        ).first()
        if alerta_existente is not None:
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
        logger.info(
            "[ALERTA] Creada: equipo_id=%d tipo=%s mensaje=%s nivel=%s",
            lectura.equipo_id,
            tipo_alerta,
            mensaje_alerta,
            "alto",
        )

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


def count_alertas(
    db: Session,
    equipo_id: int | None = None,
) -> dict[str, int]:
    """Cuenta alertas totales y no leídas para badges de UI."""

    total_query = select(func.count(Alerta.id))
    unread_query = select(func.count(Alerta.id)).where(Alerta.leida.is_(False))

    if equipo_id is not None:
        total_query = total_query.where(Alerta.equipo_id == equipo_id)
        unread_query = unread_query.where(Alerta.equipo_id == equipo_id)

    total = int(db.scalar(total_query) or 0)
    no_leidas = int(db.scalar(unread_query) or 0)
    return {"total": total, "no_leidas": no_leidas}


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
    """
    Intenta enviar email para alertas críticas ya persistidas reutilizando conexión.

    NOTA: Esta función ejecuta I/O bloqueante (SMTP) y debe ser llamada
    desde un contexto apropiado (thread separado o worker externo).
    """

    if not isinstance(db, Session):
        raise TypeError("db debe ser una instancia de SQLAlchemy Session")

    alertas_a_enviar = [a for a in alertas if a.nivel == "alto"]
    if not alertas_a_enviar:
        return

    try:
        with get_smtp_client() as smtp_client:
            for alerta in alertas_a_enviar:
                try:
                    email_result = send_alert_email_with_client(
                        smtp_client,
                        "Alerta crítica ManttoAI",
                        (
                            f"Equipo {alerta.equipo_id}: {alerta.mensaje}. "
                            f"Tipo de alerta: {alerta.tipo}."
                        ),
                    )
                    alerta.email_enviado = email_result.sent
                    if email_result.error:
                        logger.warning(
                            "[ALERTA][EMAIL] Error al enviar email para alerta_id=%s equipo_id=%s: %s",
                            alerta.id,
                            alerta.equipo_id,
                            email_result.error,
                        )
                    else:
                        logger.info(
                            "[ALERTA][EMAIL] Email enviado para alerta_id=%s equipo_id=%s subject=Alerta crítica ManttoAI",
                            alerta.id,
                            alerta.equipo_id,
                        )
                except (RuntimeError, OSError, SMTPException) as exc:
                    # Registrar tipo y mensaje para diagnóstico sin volcar posibles
                    # credenciales SMTP. En staging/DEBUG habilitar exc_info=True.
                    logger.warning(
                        "Falla inesperada en envío de email para alerta_id=%s: %s: %s",
                        alerta.id,
                        type(exc).__name__,
                        str(exc),
                    )
                    alerta.email_enviado = False
    except (RuntimeError, OSError, SMTPException) as exc:
        logger.warning(
            "No se pudo establecer conexión SMTP para notificaciones: %s: %s",
            type(exc).__name__,
            str(exc),
        )
        for alerta in alertas_a_enviar:
            alerta.email_enviado = False

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("No se pudo persistir estado de emails de alertas")
        raise


def _dispatch_emails_in_thread(
    alerta_ids: list[int], factory: Callable[[], Session]
) -> None:
    """
    Worker que corre en hilo separado para enviar emails sin bloquear el worker ASGI.

    Abre su propia sesión de BD y ejecuta el envío SMTP bloqueante de forma aislada.
    """

    db = factory()
    try:
        alertas = list(db.scalars(select(Alerta).where(Alerta.id.in_(alerta_ids))))
        dispatch_critical_email_notifications(db, alertas)
    except (SQLAlchemyError, RuntimeError, OSError, SMTPException) as exc:
        logger.warning(
            "Error en envío de emails en hilo de fondo: %s: %s",
            type(exc).__name__,
            str(exc),
        )
    finally:
        db.close()


def dispatch_critical_email_notifications_bg(
    alerta_ids: list[int],
    session_factory: Callable[[], Session] | None = None,
) -> None:
    """
    Versión para BackgroundTasks que delega el envío a un hilo separado.

    Evita bloquear el worker ASGI al ejecutar I/O SMTP bloqueante en un thread daemon.

    En entornos de testing (SQLite en memoria), ejecuta sincrónicamente para evitar
    race conditions en los tests.
    """

    if not alerta_ids:
        return

    if session_factory is not None and not callable(session_factory):
        raise TypeError("session_factory debe ser callable que retorna una Session")

    factory = session_factory or SessionLocal

    # En modo test (SQLite en memoria), ejecutar sincrónicamente
    # para evitar race conditions con threads daemon
    from app.config import get_settings

    settings = get_settings()
    is_testing = (
        "sqlite" in settings.database_url.lower()
        and ":memory:" in settings.database_url.lower()
    )

    if is_testing:
        # Ejecución síncrona en tests
        _dispatch_emails_in_thread(alerta_ids, factory)
    else:
        # Ejecución async en producción
        thread = threading.Thread(
            target=_dispatch_emails_in_thread,
            args=(alerta_ids, factory),
            daemon=True,
            name=f"smtp-worker-{alerta_ids[0] if alerta_ids else 'empty'}",
        )
        thread.start()


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
        logger.info(
            "[ALERTA] Predicción creada (sin commit): equipo_id=%d probabilidad=%.2f",
            equipo_id,
            probabilidad,
        )
        return alerta

    try:
        db.flush()  # Intentar persistir en la transacción actual para detectar duplicados
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning(
            "[ALERTA] Predicción duplicada no creada: equipo_id=%d",
            equipo_id,
        )
        return get_active_prediction_failure_alert(db, equipo_id)
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(alerta)
    dispatch_critical_email_notifications(db, [alerta])
    return alerta
