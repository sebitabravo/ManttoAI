"""Servicios de SLA (Service Level Agreement) — uptime, downtime y reportes mensuales."""

import logging
from calendar import monthrange
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.sla import SLAEvent, SLAReport
from app.services.common import get_entity_or_404

logger = logging.getLogger(__name__)

# Fracción de mes (en días) desde el final para emitir advertencia temprana
WARNING_DAYS_EARLY = 3
# Umbral de alerta temprana para cumplimiento SLA proyectado (porcentaje)
WARNING_THRESHOLD = 99.0
# Penalización base por incumplimiento SLA (valor ejemplar; se puede parametrizar)
DEFAULT_CREDIT_RATE = 0.05  # 5 % del valor mensual


def _seconds_in_month(month_str: str) -> int:
    """Retorna la cantidad total de segundos en un mes dado (formato 'YYYY-MM')."""
    year_s, month_s = month_str.split("-")
    year = int(year_s)
    month = int(month_s)
    _, days_in_month = monthrange(year, month)
    return days_in_month * 86_400


def _parse_month_boundaries(month_str: str) -> tuple[datetime, datetime]:
    """Retorna (inicio_del_mes, inicio_del_siguiente_mes) como datetimes timezone-aware UTC."""
    year_s, month_s = month_str.split("-")
    year = int(year_s)
    month = int(month_s)
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    next_year = year + 1 if month == 12 else year
    next_month = 1 if month == 12 else month + 1
    end = datetime(next_year, next_month, 1, tzinfo=timezone.utc)
    return start, end


def _days_remaining_in_month() -> int:
    """Retorna los días que quedan desde hoy hasta el fin del mes actual (sin contar hoy)."""
    today = date.today()
    _, last_day = monthrange(today.year, today.month)
    last_date = date(today.year, today.month, last_day)
    remaining = (last_date - today).days
    return remaining if remaining >= 0 else 0


def _current_month_str() -> str:
    """Retorna el mes actual en formato 'YYYY-MM'."""
    today = date.today()
    return today.strftime("%Y-%m")


def calculate_uptime(org_id: int, month_str: str, db: Session) -> dict:
    """
    Calcula el porcentaje de uptime de una organizacion en un mes determinado.

    Parametros
    ----------
    org_id : int
        Identificador de la organizacion.
    month_str : str
        Mes en formato 'YYYY-MM' (ej: '2026-06').
    db : Session
        Sesion activa de SQLAlchemy.

    Retorna
    -------
    dict
        Contiene uptime_percentage, downtime_seconds, total_seconds, met_sla,
        sla_target y el mes consultado.
    """
    start_dt, end_dt = _parse_month_boundaries(month_str)
    total_seconds = _seconds_in_month(month_str)

    # Sumar downtime del mes con eventos que ya terminaron o aun activos
    # (si no ha terminado, se considera desde started_at hasta ahora o hasta
    # fin de mes, lo que sea menor)
    now = datetime.now(timezone.utc)
    cutoff = min(now, end_dt)

    stmt = select(func.coalesce(func.sum(SLAEvent.duration_seconds), 0)).where(
        SLAEvent.organizacion_id == org_id,
        SLAEvent.started_at < end_dt,
        # Solo eventos cuyo inicio cae dentro del mes; si ya termino
        # debe haber terminado despues del inicio del mes
        SLAEvent.started_at >= start_dt,
    )
    total_downtime = int(db.scalar(stmt) or 0)

    # Considerar eventos activos (sin ended_at) que empezaron este mes
    stmt_active = select(SLAEvent).where(
        SLAEvent.organizacion_id == org_id,
        SLAEvent.started_at >= start_dt,
        SLAEvent.started_at < end_dt,
        SLAEvent.ended_at.is_(None),
    )
    for event in db.scalars(stmt_active):
        event_start = event.started_at.replace(tzinfo=timezone.utc)
        running_seconds = int((cutoff - event_start).total_seconds())
        if running_seconds > 0:
            total_downtime += running_seconds

    # Considerar eventos que empezaron antes del mes pero siguen activos
    stmt_carryover = select(SLAEvent).where(
        SLAEvent.organizacion_id == org_id,
        SLAEvent.started_at < start_dt,
        SLAEvent.ended_at.is_(None),
    )
    for event in db.scalars(stmt_carryover):
        carry_seconds = int((cutoff - start_dt).total_seconds())
        if carry_seconds > 0:
            total_downtime += carry_seconds

    # Considerar eventos que empezaron antes y terminaron dentro del mes
    stmt_carryover_closed = select(SLAEvent).where(
        SLAEvent.organizacion_id == org_id,
        SLAEvent.started_at < start_dt,
        SLAEvent.ended_at >= start_dt,
        SLAEvent.ended_at < end_dt,
    )
    for event in db.scalars(stmt_carryover_closed):
        effective_end = event.ended_at.replace(tzinfo=timezone.utc)
        carry_seconds = int((effective_end - start_dt).total_seconds())
        if carry_seconds > 0:
            total_downtime += carry_seconds

    uptime_seconds = max(total_seconds - total_downtime, 0)
    uptime_pct = round((uptime_seconds / total_seconds) * 100, 4) if total_seconds > 0 else 100.0

    # Buscar SLA target desde el ultimo reporte del mes, o default 99.9 %
    sla_target = 99.9
    report_stmt = (
        select(SLAReport)
        .where(SLAReport.organizacion_id == org_id, SLAReport.month == month_str)
        .order_by(SLAReport.created_at.desc())
        .limit(1)
    )
    latest_report = db.scalars(report_stmt).first()
    if latest_report is not None:
        sla_target = latest_report.sla_target

    met_sla = uptime_pct >= sla_target

    return {
        "organizacion_id": org_id,
        "month": month_str,
        "uptime_percentage": uptime_pct,
        "downtime_seconds": total_downtime,
        "total_seconds": total_seconds,
        "sla_target": sla_target,
        "met_sla": met_sla,
    }


def log_downtime_event(
    db: Session,
    org_id: int,
    event_type: str,
    cause: str,
    started_at: datetime | None = None,
    equipo_id: int | None = None,
) -> SLAEvent:
    """
    Registra el inicio de un evento de downtime (outage, degradacion, mantenimiento).

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.
    org_id : int
        Identificador de la organizacion.
    event_type : str
        Tipo de evento: 'outage', 'degraded', 'maintenance'.
    cause : str
        Descripcion de la causa del downtime.
    started_at : datetime | None
        Momento de inicio del evento. Si es None, se usa la hora actual UTC.
    equipo_id : int | None
        Identificador opcional del equipo afectado.

    Retorna
    -------
    SLAEvent
        El evento de downtime recien creado.
    """
    if event_type not in ("outage", "degraded", "maintenance"):
        raise ValueError(
            f"event_type debe ser 'outage', 'degraded' o 'maintenance'; se recibio '{event_type}'"
        )

    if started_at is None:
        started_at = datetime.now(timezone.utc)

    event = SLAEvent(
        organizacion_id=org_id,
        equipo_id=equipo_id,
        event_type=event_type,
        started_at=started_at,
        cause=cause,
    )
    db.add(event)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "[SLA] Error al registrar evento de downtime: org_id=%d type=%s",
            org_id,
            event_type,
        )
        raise

    db.refresh(event)
    logger.info(
        "[SLA] Downtime registrado: id=%d org_id=%d type=%s cause=%s started_at=%s",
        event.id,
        event.organizacion_id,
        event.event_type,
        event.cause,
        event.started_at.isoformat(),
    )
    return event


def resolve_downtime_event(
    db: Session,
    event_id: int,
    ended_at: datetime | None = None,
) -> SLAEvent:
    """
    Cierra un evento de downtime y calcula su duracion en segundos.

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.
    event_id : int
        Identificador del evento a cerrar.
    ended_at : datetime | None
        Momento de fin del evento. Si es None, se usa la hora actual UTC.

    Retorna
    -------
    SLAEvent
        El evento actualizado con ended_at y duration_seconds.
    """
    event = get_entity_or_404(db, SLAEvent, event_id, "Evento SLA no encontrado")

    if event.ended_at is not None:
        logger.warning(
            "[SLA] Evento ya estaba cerrado: id=%d ended_at=%s",
            event.id,
            event.ended_at.isoformat(),
        )

    if ended_at is None:
        ended_at = datetime.now(timezone.utc)

    event.ended_at = ended_at

    # Calcular duracion usando timezone-aware
    start = event.started_at
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    end = ended_at
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    duration = int((end - start).total_seconds())
    event.duration_seconds = max(duration, 0)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "[SLA] Error al resolver evento de downtime: id=%d",
            event_id,
        )
        raise

    db.refresh(event)
    logger.info(
        "[SLA] Downtime resuelto: id=%d duration=%ds ended_at=%s",
        event.id,
        event.duration_seconds,
        event.ended_at.isoformat(),
    )
    return event


def generate_monthly_report(
    db: Session,
    org_id: int,
    month_str: str,
    sla_target: float | None = None,
    credit_rate: float | None = None,
) -> SLAReport:
    """
    Genera un reporte mensual de cumplimiento SLA para una organizacion.

    Calcula el uptime real del mes y crea un registro persistente con el
    resultado, incluyendo si se cumplio el SLA objetivo y el monto de
    creditos de penalizacion si aplica.

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.
    org_id : int
        Identificador de la organizacion.
    month_str : str
        Mes en formato 'YYYY-MM' (ej: '2026-06').
    sla_target : float | None
        Porcentaje minimo de uptime requerido (ej: 99.9). Si es None,
        se intenta leer del ultimo reporte del mismo mes o se usa 99.9.
    credit_rate : float | None
        Fraccion del valor mensual a creditar por cada 1 % de
        incumplimiento. Default: 0.05 (5 %).

    Retorna
    -------
    SLAReport
        El reporte mensual recien creado.
    """
    if sla_target is None:
        sla_target = 99.9
    if credit_rate is None:
        credit_rate = DEFAULT_CREDIT_RATE

    uptime_data = calculate_uptime(org_id, month_str, db)
    uptime_pct = uptime_data["uptime_percentage"]
    downtime_seconds = uptime_data["downtime_seconds"]
    total_seconds = uptime_data["total_seconds"]
    met_sla = uptime_pct >= sla_target

    # Calcular creditos: si no se cumple, se penaliza segun la fraccion
    # de incumplimiento
    credits_amount = 0.0
    if not met_sla:
        shortfall = sla_target - uptime_pct
        credits_amount = round(shortfall * credit_rate, 4)

    report = SLAReport(
        organizacion_id=org_id,
        month=month_str,
        total_seconds=total_seconds,
        downtime_seconds=downtime_seconds,
        uptime_percentage=uptime_pct,
        sla_target=sla_target,
        met_sla=met_sla,
        credits_amount=credits_amount,
    )
    db.add(report)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "[SLA] Error al generar reporte mensual: org_id=%d month=%s",
            org_id,
            month_str,
        )
        raise

    db.refresh(report)
    logger.info(
        "[SLA] Reporte generado: id=%d org_id=%d month=%s uptime=%.2f%% met_sla=%s credits=%.4f",
        report.id,
        report.organizacion_id,
        report.month,
        report.uptime_percentage,
        report.met_sla,
        report.credits_amount,
    )
    return report


def get_current_uptime_status(db: Session, org_id: int) -> dict:
    """
    Retorna el estado actual de uptime de una organizacion.

    Incluye eventos activos, ultimos eventos resueltos y el uptime
    del mes en curso.

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.
    org_id : int
        Identificador de la organizacion.

    Retorna
    -------
    dict
        Contiene is_healthy (bool), active_events (list), recent_events (list),
        current_month_uptime (dict) y active_event_count (int).
    """
    current_month = _current_month_str()

    # Eventos activos (sin ended_at)
    stmt_active = (
        select(SLAEvent)
        .where(
            SLAEvent.organizacion_id == org_id,
            SLAEvent.ended_at.is_(None),
        )
        .order_by(SLAEvent.started_at.desc())
    )
    active_events = list(db.scalars(stmt_active))

    # Ultimos 10 eventos resueltos
    stmt_recent = (
        select(SLAEvent)
        .where(
            SLAEvent.organizacion_id == org_id,
            SLAEvent.ended_at.is_not(None),
        )
        .order_by(SLAEvent.ended_at.desc())
        .limit(10)
    )
    recent_events = list(db.scalars(stmt_recent))

    # Uptime del mes actual
    uptime_data = calculate_uptime(org_id, current_month, db)

    # Serializar eventos como dicts
    def _serialize_event(event: SLAEvent) -> dict:
        return {
            "id": event.id,
            "organizacion_id": event.organizacion_id,
            "equipo_id": event.equipo_id,
            "event_type": event.event_type,
            "cause": event.cause,
            "started_at": event.started_at.isoformat() if event.started_at else None,
            "ended_at": event.ended_at.isoformat() if event.ended_at else None,
            "duration_seconds": event.duration_seconds,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }

    return {
        "organizacion_id": org_id,
        "is_healthy": len(active_events) == 0,
        "active_event_count": len(active_events),
        "active_events": [_serialize_event(e) for e in active_events],
        "recent_events": [_serialize_event(e) for e in recent_events],
        "current_month_uptime": uptime_data,
    }


def check_sla_compliance(db: Session, org_id: int) -> dict:
    """
    Verifica el cumplimiento SLA y emite alerta temprana si se proyecta
    un incumplimiento faltando 3 o menos dias para fin de mes.

    Evalua el uptime actual y lo proyecta al resto del mes. Si la
    proyeccion cae bajo WARNING_THRESHOLD (99 %) con
    WARNING_DAYS_EARLY (3) dias o menos restantes, se genera una
    alerta en el dict de retorno.

    Parametros
    ----------
    db : Session
        Sesion activa de SQLAlchemy.
    org_id : int
        Identificador de la organizacion.

    Retorna
    -------
    dict
        Contiene compliant (bool), current_uptime_percentage (float),
        sla_target (float), days_remaining (int), warning (bool),
        warning_message (str | None), projected_uptime (float | None).
    """
    current_month = _current_month_str()
    uptime_data = calculate_uptime(org_id, current_month, db)
    uptime_pct = uptime_data["uptime_percentage"]
    sla_target = uptime_data["sla_target"]
    days_left = _days_remaining_in_month()
    total_downtime = uptime_data["downtime_seconds"]
    total_seconds = uptime_data["total_seconds"]

    # Proyectar uptime al final del mes asumiendo que no habra mas downtime
    projected_uptime = uptime_pct
    warning = False
    warning_message = None

    # Si quedan pocos dias, chequear si el uptime actual ya esta peligrosamente bajo
    if days_left <= WARNING_DAYS_EARLY and uptime_pct < WARNING_THRESHOLD:
        warning = True
        # Calcular cuantos segundos adicionales de downtime "gratis" quedan
        # antes de incumplir el SLA target
        max_allowed_downtime = total_seconds * ((100.0 - sla_target) / 100.0)
        remaining_budget = max_allowed_downtime - total_downtime

        warning_message = (
            f"El uptime actual es {uptime_pct:.2f} %, por debajo del "
            f"umbral de alerta temprana ({WARNING_THRESHOLD} %). "
            f"Quedan {days_left} dias en el mes y el margen restante de "
            f"downtime antes de incumplir el SLA ({sla_target} %) es de "
            f"aproximadamente {max(remaining_budget, 0)} segundos."
        )

        logger.warning(
            "[SLA] Alerta temprana de cumplimiento: org_id=%d uptime=%.2f%% target=%.2f%% days_left=%d",
            org_id,
            uptime_pct,
            sla_target,
            days_left,
        )

    compliant = uptime_pct >= sla_target

    return {
        "organizacion_id": org_id,
        "month": current_month,
        "compliant": compliant,
        "current_uptime_percentage": uptime_pct,
        "sla_target": sla_target,
        "total_downtime_seconds": total_downtime,
        "days_remaining": days_left,
        "warning": warning,
        "warning_message": warning_message,
        "projected_uptime": projected_uptime,
    }
