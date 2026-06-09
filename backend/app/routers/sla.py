"""Endpoints de SLA (Service Level Agreement) — uptime, downtime y reportes mensuales."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.sla import SLAEvent, SLAReport
from app.models.usuario import Usuario
from app.schemas.sla import (
    SLAEventCreate,
    SLAEventResolve,
    SLAEventResponse,
    SLAReportResponse,
)
from app.services import sla_service

router = APIRouter(prefix="/sla", tags=["sla"])


@router.get("/status")
def get_sla_status(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico", "visualizador")),
) -> dict:
    """Retorna el estado actual de uptime de la organizacion del usuario.

    Incluye eventos activos, ultimos eventos resueltos y uptime del mes en curso.
    """
    org_id = getattr(current_user, "organizacion_id", None)
    return sla_service.get_current_uptime_status(db, org_id)


@router.get(
    "/events",
    response_model=list[SLAEventResponse],
)
def get_sla_events(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico", "visualizador")),
    limit: int = Query(default=50, ge=1, le=500),
    event_type: str | None = Query(default=None),
) -> list[SLAEventResponse]:
    """Lista eventos de downtime recientes de la organizacion.

    Filtra automaticamente por la organizacion del usuario autenticado.
    Soporta filtro opcional por tipo de evento (outage, degraded, maintenance).
    """
    org_id = getattr(current_user, "organizacion_id", None)

    stmt = select(SLAEvent).where(SLAEvent.organizacion_id == org_id)

    if event_type is not None:
        stmt = stmt.where(SLAEvent.event_type == event_type)

    stmt = stmt.order_by(SLAEvent.started_at.desc()).limit(limit)

    return list(db.scalars(stmt))


@router.get(
    "/reports",
    response_model=list[SLAReportResponse],
)
def get_sla_reports(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico", "visualizador")),
    limit: int = Query(default=12, ge=1, le=60),
) -> list[SLAReportResponse]:
    """Lista reportes mensuales de SLA de la organizacion, ordenados del mas reciente al mas antiguo."""
    org_id = getattr(current_user, "organizacion_id", None)

    stmt = (
        select(SLAReport)
        .where(SLAReport.organizacion_id == org_id)
        .order_by(SLAReport.month.desc())
        .limit(limit)
    )

    return list(db.scalars(stmt))


@router.get(
    "/reports/{month}",
    response_model=SLAReportResponse,
)
def get_sla_report_by_month(
    month: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico", "visualizador")),
) -> SLAReportResponse:
    """Retorna el reporte SLA de un mes especifico (formato 'YYYY-MM')."""
    org_id = getattr(current_user, "organizacion_id", None)

    stmt = select(SLAReport).where(
        SLAReport.organizacion_id == org_id,
        SLAReport.month == month,
    )
    report = db.scalars(stmt).first()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado para el mes especificado",
        )
    return SLAReportResponse.model_validate(report)


@router.post(
    "/events",
    response_model=SLAEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_sla_event(
    payload: SLAEventCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> SLAEventResponse:
    """Registra manualmente un evento de downtime (solo admin)."""
    org_id = getattr(current_user, "organizacion_id", None)

    return sla_service.log_downtime_event(
        db,
        org_id=org_id,
        event_type=payload.event_type,
        cause=payload.cause,
        started_at=payload.started_at,
        equipo_id=payload.equipo_id,
    )


@router.patch(
    "/events/{event_id}/resolve",
    response_model=SLAEventResponse,
)
def patch_sla_event_resolve(
    event_id: int,
    payload: SLAEventResolve,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> SLAEventResponse:
    """Resuelve un evento de downtime manualmente (solo admin)."""
    return sla_service.resolve_downtime_event(
        db,
        event_id=event_id,
        ended_at=payload.ended_at,
    )
