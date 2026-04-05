"""Endpoints de predicciones."""

from fastapi import APIRouter

from app.schemas.prediccion import PrediccionResponse
from app.services.prediccion_service import execute_prediction, get_prediction

router = APIRouter(prefix="/predicciones", tags=["predicciones"])


@router.get("/{equipo_id}", response_model=PrediccionResponse)
def get_prediccion(equipo_id: int) -> PrediccionResponse:
    """Obtiene la última predicción demo de un equipo."""

    return get_prediction(equipo_id)


@router.post("/ejecutar/{equipo_id}", response_model=PrediccionResponse)
def post_prediccion(equipo_id: int) -> PrediccionResponse:
    """Ejecuta una predicción demo para el equipo."""

    return execute_prediction(equipo_id)
