"""Endpoints de lecturas."""

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.middleware.rate_limit import limiter
from app.schemas.lectura import LecturaCreate, LecturaResponse
from app.services.lectura_service import (
    create_lectura,
    get_latest_lectura,
    list_lecturas,
)

router = APIRouter(prefix="/lecturas", tags=["lecturas"])


@router.get(
    "",
    response_model=list[LecturaResponse],
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
@limiter.limit("500/minute")
def get_lecturas(
    request: Request,
    equipo_id: int | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> list[LecturaResponse]:
    """Entrega historial persistido de lecturas con límite por defecto."""

    return list_lecturas(db, equipo_id, limit)


@router.get(
    "/latest/{equipo_id}",
    response_model=LecturaResponse,
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
@limiter.limit("500/minute")
def get_latest(
    equipo_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> LecturaResponse:
    """Entrega la última lectura persistida de un equipo."""

    return get_latest_lectura(db, equipo_id)


@router.post(
    "",
    response_model=LecturaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin", "tecnico"))],
)
@limiter.limit("1000/hour")  # Más alto para IoT
def post_lectura(
    payload: LecturaCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> LecturaResponse:
    """Crea una lectura persistida."""

    # Permite inyectar session_factory en tests sin tocar la DB de producción
    session_factory = getattr(request.app.state, "testing_session_local", None)
    return create_lectura(
        db, payload, background_tasks=background_tasks, session_factory=session_factory
    )
