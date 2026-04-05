"""Servicios de equipos."""

from app.schemas.equipo import EquipoCreate, EquipoResponse, EquipoUpdate

DEMO_EQUIPOS = [
    EquipoResponse(
        id=1,
        nombre="Compresor principal",
        ubicacion="Taller",
        tipo="Compresor",
        estado="operativo",
    ),
    EquipoResponse(
        id=2,
        nombre="Motor bomba",
        ubicacion="Laboratorio",
        tipo="Motor",
        estado="monitoreo",
    ),
]


def list_equipos() -> list[EquipoResponse]:
    """Lista equipos demo del scaffold."""

    return DEMO_EQUIPOS


def get_equipo(equipo_id: int) -> EquipoResponse:
    """Entrega un equipo demo por identificador."""

    return next(
        (equipo for equipo in DEMO_EQUIPOS if equipo.id == equipo_id), DEMO_EQUIPOS[0]
    )


def create_equipo(payload: EquipoCreate) -> EquipoResponse:
    """Crea una representación en memoria de un equipo."""

    return EquipoResponse(id=len(DEMO_EQUIPOS) + 1, **payload.model_dump())


def update_equipo(equipo_id: int, payload: EquipoUpdate) -> EquipoResponse:
    """Actualiza un equipo demo sin persistencia real."""

    actual = get_equipo(equipo_id).model_dump()
    actual.update(
        {key: value for key, value in payload.model_dump().items() if value is not None}
    )
    return EquipoResponse(**actual)
