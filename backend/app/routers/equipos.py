"""Endpoints de equipos."""

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.middleware.rate_limit import limiter
from app.models.usuario import Usuario
from app.schemas.equipo import (
    EquipoCreate,
    EquipoFullSetupRequest,
    EquipoFullSetupResponse,
    EquipoResponse,
    EquipoUpdate,
)
from app.services.equipo_service import (
    create_equipo,
    delete_equipo,
    get_equipo_or_404,
    list_equipos,
    update_equipo,
)

router = APIRouter(prefix="/equipos", tags=["equipos"])


@router.get(
    "",
    response_model=list[EquipoResponse],
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
def get_equipos(
    request: Request,
    db: Session = Depends(get_db),
) -> list[EquipoResponse]:
    """Lista equipos disponibles."""

    return list_equipos(db)


@router.get(
    "/{equipo_id}",
    response_model=EquipoResponse,
    dependencies=[Depends(require_role("admin", "tecnico", "visualizador"))],
)
def get_equipo_by_id(
    equipo_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> EquipoResponse:
    """Obtiene un equipo por identificador."""

    return get_equipo_or_404(db, equipo_id)


@router.post(
    "",
    response_model=EquipoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin", "tecnico"))],
)
def post_equipo(
    payload: EquipoCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> EquipoResponse:
    """Crea un equipo persistido."""

    equipo = create_equipo(db, payload)
    response.headers["Location"] = str(
        request.url_for("get_equipo_by_id", equipo_id=str(equipo.id))
    )
    return equipo


@router.put(
    "/{equipo_id}",
    response_model=EquipoResponse,
    dependencies=[Depends(require_role("admin", "tecnico"))],
)
def put_equipo(
    equipo_id: int,
    payload: EquipoUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> EquipoResponse:
    """Actualiza un equipo persistido."""

    return update_equipo(db, equipo_id, payload)


@router.delete(
    "/{equipo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
def delete_equipo_by_id(
    equipo_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    """Elimina un equipo por identificador."""

    delete_equipo(db, equipo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/full-setup",
    response_model=EquipoFullSetupResponse,
    dependencies=[Depends(require_role("admin", "tecnico"))],
)
def create_equipo_with_umbrales(
    payload: EquipoFullSetupRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico")),
) -> EquipoFullSetupResponse:
    """Crea equipo con umbrales en una sola transacción atómica.

    El context manager db.begin() hace commit automáticamente al salir,
    o rollback si hay cualquier excepción.
    """
    from app.models.equipo import Equipo
    from app.models.umbral import Umbral

    # Transacción atómica: commit automático al salir, rollback si falla
    with db.begin():
        # 1. Crear equipo
        equipo = Equipo(
            nombre=payload.nombre,
            ubicacion=payload.ubicacion or "Laboratorio",
            tipo=payload.tipo or "Motor",
            descripcion=payload.descripcion or "Equipo monitoreado por ManttoAI",
            estado="operativo",
        )
        db.add(equipo)
        db.flush()  # Obtener ID

        # 2. Crear umbral de temperatura
        umbral_temp = Umbral(
            equipo_id=equipo.id,
            variable="temperatura",
            valor_min=0,
            valor_max=payload.temperatura_max,
        )
        db.add(umbral_temp)
        db.flush()

        # 3. Crear umbral de vibración
        umbral_vib = Umbral(
            equipo_id=equipo.id,
            variable="vibracion",
            valor_min=0,
            valor_max=payload.vibracion_max,
        )
        db.add(umbral_vib)
        db.flush()

    # db.begin() hace commit automático al salir del bloque
    return EquipoFullSetupResponse(
        equipo=equipo,
        umbral_temperatura_id=umbral_temp.id,
        umbral_vibracion_id=umbral_vib.id,
    )
