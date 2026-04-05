"""Endpoints de alertas."""

from fastapi import APIRouter

from app.schemas.alerta import AlertaResponse
from app.services.alerta_service import list_alertas, mark_as_read

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("", response_model=list[AlertaResponse])
def get_alertas() -> list[AlertaResponse]:
    """Lista alertas activas demo."""

    return list_alertas()


@router.patch("/{alerta_id}/leer")
def patch_alerta(alerta_id: int) -> dict[str, int | bool]:
    """Marca una alerta como leída."""

    return mark_as_read(alerta_id)
