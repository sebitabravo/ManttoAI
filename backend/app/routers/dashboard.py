"""Endpoints del dashboard."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.middleware.rate_limit import limiter
from app.schemas.dashboard import DashboardResumenResponse
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/resumen",
    response_model=DashboardResumenResponse,
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
@limiter.limit("200/hour")
def get_resumen(
    request: Request,
    db: Session = Depends(get_db),
) -> DashboardResumenResponse:
    """Entrega el resumen agregado usado por el frontend."""

    return get_dashboard_summary(db)
