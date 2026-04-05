"""Endpoints de mantenciones."""

from fastapi import APIRouter

from app.schemas.mantencion import (
    MantencionCreate,
    MantencionResponse,
    MantencionUpdate,
)

router = APIRouter(prefix="/mantenciones", tags=["mantenciones"])


@router.get("", response_model=list[MantencionResponse])
def get_mantenciones() -> list[MantencionResponse]:
    """Lista mantenciones demo."""

    return [
        MantencionResponse(
            id=1,
            equipo_id=1,
            tipo="preventiva",
            descripcion="Revisión mensual",
            estado="programada",
        )
    ]


@router.post("", response_model=MantencionResponse)
def post_mantencion(payload: MantencionCreate) -> MantencionResponse:
    """Crea una mantención demo."""

    return MantencionResponse(id=2, **payload.model_dump())


@router.put("/{mantencion_id}", response_model=MantencionResponse)
def put_mantencion(mantencion_id: int, payload: MantencionUpdate) -> MantencionResponse:
    """Actualiza una mantención demo."""

    data = {
        "equipo_id": 1,
        "tipo": "preventiva",
        "descripcion": "Revisión mensual",
        "estado": "programada",
    }
    data.update(
        {key: value for key, value in payload.model_dump().items() if value is not None}
    )
    return MantencionResponse(id=mantencion_id, **data)
