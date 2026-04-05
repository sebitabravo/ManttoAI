"""Schemas de lecturas."""

from datetime import datetime

from pydantic import BaseModel


class LecturaBase(BaseModel):
    """Campos base de lectura."""

    equipo_id: int
    temperatura: float
    humedad: float
    vib_x: float
    vib_y: float
    vib_z: float


class LecturaMqttPayload(BaseModel):
    """Payload esperado cuando llega una lectura por MQTT."""

    temperatura: float
    humedad: float
    vib_x: float
    vib_y: float
    vib_z: float
    timestamp: datetime | None = None


class LecturaCreate(LecturaBase):
    """Payload para crear lectura."""

    timestamp: datetime | None = None


class LecturaResponse(LecturaBase):
    """Representación pública de lectura."""

    id: int
    timestamp: datetime

    model_config = {"from_attributes": True}
