"""Servicios de alertas y evaluación básica de umbrales."""

import logging
from concurrent.futures import ThreadPoolExecutor
from smtplib import SMTPException

from collections.abc import Callable
from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.alerta import Alerta
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.umbral import Umbral
from app.database import SessionLocal
from app.services.email_service import (
    get_smtp_client,
    send_alert_email_with_client,
)
from app.services.tenant_scope import (
    UNSCOPED,
    add_organization_scope,
    resolve_organization_id,
)

PREDICTION_ALERT_TYPE = "prediccion"
logger = logging.getLogger(__name__)
_SMTP_EXECUTOR = ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix="smtp-worker",
)


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


def _resolve_equipo_scope(
    db: Session, equipo_id: int, organization_id: int | None | object = UNSCOPED
) -> int | None | object:
    """Obtiene el tenant del equipo para workers que no tienen request."""

    resolved_id = resolve_organization_id(db, organization_id)
    if resolved_id is not UNSCOPED:
        return resolved_id

    equipo = db.get(Equipo, equipo_id)
    return equipo.organizacion_id if equipo is not None else UNSCOPED


def evaluate_thresholds(
    db: Session,
    lectura: Lectura,
    organization_id: int | None | object = UNSCOPED,
) -> list[Alerta]:
    """Evalúa umbrales y agrega alertas en sesión; el caller realiza commit."""

    _lock_equipo_alert_scope(db, lectura.equipo_id)
    scope_id = _resolve_equipo_scope(db, lectura.equipo_id, organization_id)
    umbral_query = (
        select(Umbral)
        .join(Equipo, Equipo.id == Umbral.equipo_id)
        .where(Umbral.equipo_id == lectura.equipo_id)
    )
    umbrales = list(
        db.scalars(
            add_organization_scope(umbral_query, Equipo.organizacion_id, db, scope_id)
        )
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
        # NOTA: Usamos with_for_update() para romper el snapshot isolation en MySQL
        # y ver alertas creadas por transacciones concurrentes recién confirmadas.
        alerta_query = (
            select(Alerta)
            .join(Equipo, Equipo.id == Alerta.equipo_id)
            .where(Alerta.equipo_id == lectura.equipo_id)
            .where(Alerta.tipo == tipo_alerta)
            .where(Alerta.mensaje == mensaje_alerta)
            .where(Alerta.leida.is_(False))
            .with_for_update()
            .limit(1)
        )
        alerta_existente = db.scalars(
            add_organization_scope(alerta_query, Equipo.organizacion_id, db, scope_id)
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
            organizacion_id=None if scope_id is UNSCOPED else scope_id,
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
    organization_id: int | None | object = UNSCOPED,
) -> list[Alerta]:
    """Lista alertas persistidas con filtros simples de consulta."""

    query = select(Alerta).join(Equipo, Equipo.id == Alerta.equipo_id)
    if equipo_id is not None:
        query = query.where(Alerta.equipo_id == equipo_id)
    if solo_no_leidas:
        query = query.where(Alerta.leida.is_(False))
    query = add_organization_scope(query, Equipo.organizacion_id, db, organization_id)

    query = query.order_by(Alerta.created_at.desc(), Alerta.id.desc())
    if limite is not None:
        query = query.limit(limite)

    return list(db.scalars(query))


def count_alertas(
    db: Session,
    equipo_id: int | None = None,
    organization_id: int | None | object = UNSCOPED,
) -> dict[str, int]:
    """Cuenta alertas totales y no leídas para badges de UI."""

    total_query = select(func.count(Alerta.id)).join(
        Equipo, Equipo.id == Alerta.equipo_id
    )
    unread_query = (
        select(func.count(Alerta.id))
        .join(Equipo, Equipo.id == Alerta.equipo_id)
        .where(Alerta.leida.is_(False))
    )

    if equipo_id is not None:
        total_query = total_query.where(Alerta.equipo_id == equipo_id)
        unread_query = unread_query.where(Alerta.equipo_id == equipo_id)

    total_query = add_organization_scope(
        total_query, Equipo.organizacion_id, db, organization_id
    )
    unread_query = add_organization_scope(
        unread_query, Equipo.organizacion_id, db, organization_id
    )

    total = int(db.scalar(total_query) or 0)
    no_leidas = int(db.scalar(unread_query) or 0)
    return {"total": total, "no_leidas": no_leidas}


def get_active_prediction_failure_alert(
    db: Session,
    equipo_id: int,
    organization_id: int | None | object = UNSCOPED,
) -> Alerta | None:
    """Obtiene alerta activa de predicción para un equipo, si existe."""

    # NOTA: Usamos with_for_update() para romper el snapshot isolation en MySQL
    # y ver alertas creadas por transacciones concurrentes recién confirmadas.
    query = (
        select(Alerta)
        .join(Equipo, Equipo.id == Alerta.equipo_id)
        .where(Alerta.equipo_id == equipo_id)
        .where(Alerta.tipo == PREDICTION_ALERT_TYPE)
        .where(Alerta.nivel == "alto")
        .where(Alerta.leida.is_(False))
        .with_for_update()
        .limit(1)
    )
    scope_id = _resolve_equipo_scope(db, equipo_id, organization_id)
    return db.scalars(
        add_organization_scope(query, Equipo.organizacion_id, db, scope_id)
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


def get_alerta_or_404(
    db: Session, alerta_id: int, organization_id: int | None | object = UNSCOPED
) -> Alerta:
    """Obtiene una alerta por id o retorna 404 si no existe."""

    from fastapi import HTTPException, status

    query = add_organization_scope(
        select(Alerta)
        .join(Equipo, Equipo.id == Alerta.equipo_id)
        .where(Alerta.id == alerta_id),
        Equipo.organizacion_id,
        db,
        organization_id,
    )
    alerta = db.scalars(query).first()
    if alerta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada"
        )
    return alerta


def mark_as_read(
    db: Session,
    alerta_id: int,
    organization_id: int | None | object = UNSCOPED,
) -> dict[str, int | bool]:
    """Marca una alerta persistida como leída."""

    alerta = get_alerta_or_404(db, alerta_id, organization_id)
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
    run_inline: bool = False,
) -> None:
    """
    Versión para BackgroundTasks que delega el envío a un executor acotado.

    ``run_inline`` se inyecta explícitamente por el caller cuando necesita una
    ejecución síncrona (por ejemplo, una fixture de tests). La configuración de
    la base de datos no altera el comportamiento de producción.
    """

    if not alerta_ids:
        return

    if session_factory is not None and not callable(session_factory):
        raise TypeError("session_factory debe ser callable que retorna una Session")

    factory = session_factory or SessionLocal

    if run_inline:
        _dispatch_emails_in_thread(alerta_ids, factory)
    else:
        _SMTP_EXECUTOR.submit(_dispatch_emails_in_thread, alerta_ids, factory)


def create_prediction_failure_alert(
    db: Session,
    equipo_id: int,
    probabilidad: float,
    auto_commit: bool = True,
    organization_id: int | None | object = UNSCOPED,
) -> Alerta | None:
    """Crea alerta crítica por predicción de falla evitando duplicados activos."""

    _lock_equipo_alert_scope(db, equipo_id)
    scope_id = _resolve_equipo_scope(db, equipo_id, organization_id)
    alerta_activa = get_active_prediction_failure_alert(db, equipo_id, scope_id)

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
        organizacion_id=None if scope_id is UNSCOPED else scope_id,
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
        return get_active_prediction_failure_alert(db, equipo_id, scope_id)
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(alerta)
    dispatch_critical_email_notifications(db, [alerta])
    return alerta
