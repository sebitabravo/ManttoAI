"""Endpoints de predicciones."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.prediccion import PrediccionResponse
from app.services.prediccion_service import execute_prediction, get_prediction

router = APIRouter(prefix="/predicciones", tags=["predicciones"])


@router.get("/{equipo_id}", response_model=PrediccionResponse)
def get_prediccion(
    equipo_id: int,
    db: Session = Depends(get_db),
) -> PrediccionResponse:
    """Obtiene la última predicción persistida de un equipo."""

    return get_prediction(db, equipo_id)


@router.post(
    "/ejecutar/{equipo_id}",
    response_model=PrediccionResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_prediccion(
    equipo_id: int,
    db: Session = Depends(get_db),
) -> PrediccionResponse:
    """Ejecuta una predicción real para el equipo y la persiste."""

    return execute_prediction(db, equipo_id)
