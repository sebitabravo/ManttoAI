"""Endpoints del dashboard."""

from fastapi import APIRouter

from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/resumen")
def get_resumen() -> dict[str, int | float | str]:
    """Entrega el resumen agregado usado por el frontend."""

    return get_dashboard_summary()
