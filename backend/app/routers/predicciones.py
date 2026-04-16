"""Endpoints de predicciones."""

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.middleware.rate_limit import limiter
from app.schemas.prediccion import PrediccionResponse
from app.services.prediccion_service import execute_prediction, get_prediction

router = APIRouter(prefix="/predicciones", tags=["predicciones"])


@router.get(
    "/{equipo_id}",
    response_model=PrediccionResponse,
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
def get_prediccion(
    equipo_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> PrediccionResponse:
    """Obtiene la última predicción persistida de un equipo."""

    return get_prediction(db, equipo_id)


@router.post(
    "/ejecutar/{equipo_id}",
    response_model=PrediccionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin", "tecnico"))],
)
def post_prediccion(
    equipo_id: int,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> PrediccionResponse:
    """Ejecuta una predicción real para el equipo y la persiste."""

    # Permite inyectar session_factory en tests sin tocar la DB de producción
    session_factory = getattr(request.app.state, "testing_session_local", None)
    return execute_prediction(
        db,
        equipo_id,
        background_tasks=background_tasks,
        session_factory=session_factory,
    )
