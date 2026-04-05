"""Endpoints del dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/resumen")
def get_resumen(db: Session = Depends(get_db)) -> dict[str, int | float | str]:
    """Entrega el resumen agregado usado por el frontend."""

    return get_dashboard_summary(db)
