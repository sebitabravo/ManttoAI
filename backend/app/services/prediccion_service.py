"""Servicios de predicción de riesgo."""

from datetime import datetime, timezone

from app.schemas.prediccion import PrediccionResponse


def get_prediction(equipo_id: int) -> PrediccionResponse:
    """Entrega una predicción demo para el equipo solicitado."""

    return PrediccionResponse(
        id=1,
        equipo_id=equipo_id,
        clasificacion="alerta",
        probabilidad=0.68,
        modelo_version="rf-mvp",
        created_at=datetime.now(timezone.utc),
    )


def execute_prediction(equipo_id: int) -> PrediccionResponse:
    """Ejecuta una predicción demo reutilizando el resultado base."""

    return get_prediction(equipo_id)
