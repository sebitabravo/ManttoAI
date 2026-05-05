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
@limiter.limit("6000/minute")  # Alto volume para dashboard polling
def get_lecturas(
    request: Request,
    equipo_id: int | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=5000),
    page: int | None = Query(default=None, ge=1),
    per_page: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[LecturaResponse]:
    """Entrega historial persistido de lecturas con paginación.

    Si se pasa `limit`, usa el comportamiento legacy (sin paginación).
    Si se pasa `page`, usa paginación con `per_page`.
    Si no se pasa ninguno, usa paginación por defecto (page=1, per_page=50).
    """

    # Retrocompatibilidad: si pasan limit explícito, usar modo legacy
    if limit is not None:
        return list_lecturas(db, equipo_id, limit=limit)

    # Paginación normal
    actual_page = page or 1
    return list_lecturas(
        db, equipo_id, limit=per_page, offset=(actual_page - 1) * per_page
    )


@router.get(
    "/latest/{equipo_id}",
    response_model=LecturaResponse,
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
@limiter.limit("6000/minute")  # Alto volume para polling frecuente
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
