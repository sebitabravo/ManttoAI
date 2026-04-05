"""Servicios de lecturas telemétricas."""

from datetime import datetime, timezone

from app.schemas.lectura import LecturaCreate, LecturaResponse


def list_lecturas(equipo_id: int | None = None) -> list[LecturaResponse]:
    """Retorna lecturas demo para pruebas de integración."""

    target_id = equipo_id or 1
    return [
        LecturaResponse(
            id=1,
            equipo_id=target_id,
            temperatura=42.5,
            humedad=58.0,
            vib_x=0.3,
            vib_y=0.2,
            vib_z=9.7,
            timestamp=datetime.now(timezone.utc),
        )
    ]


def get_latest_lectura(equipo_id: int) -> LecturaResponse:
    """Retorna la última lectura conocida del equipo."""

    return list_lecturas(equipo_id)[0]


def create_lectura(payload: LecturaCreate) -> LecturaResponse:
    """Crea una lectura demo en memoria."""

    return LecturaResponse(
        id=99, timestamp=datetime.now(timezone.utc), **payload.model_dump()
    )
