"""Schemas de lecturas."""

from datetime import datetime

from pydantic import BaseModel, Field


class LecturaBase(BaseModel):
    """Campos base de lectura."""

    equipo_id: int
    temperatura: float = Field(..., ge=-40, le=150)
    humedad: float = Field(..., ge=0, le=100)
    vib_x: float = Field(..., ge=-50, le=50)
    vib_y: float = Field(..., ge=-50, le=50)
    vib_z: float = Field(..., ge=-50, le=50)


class LecturaMqttPayload(BaseModel):
    """Payload esperado cuando llega una lectura por MQTT."""

    temperatura: float = Field(..., ge=-40, le=150)
    humedad: float = Field(..., ge=0, le=100)
    vib_x: float = Field(..., ge=-50, le=50)
    vib_y: float = Field(..., ge=-50, le=50)
    vib_z: float = Field(..., ge=-50, le=50)
    timestamp: datetime | None = None


class LecturaCreate(LecturaBase):
    """Payload para crear lectura."""

    timestamp: datetime | None = None


class LecturaUpdate(BaseModel):
    """Payload para actualizar una lectura de forma parcial."""

    temperatura: float | None = Field(default=None, ge=-40, le=150)
    humedad: float | None = Field(default=None, ge=0, le=100)
    vib_x: float | None = Field(default=None, ge=-50, le=50)
    vib_y: float | None = Field(default=None, ge=-50, le=50)
    vib_z: float | None = Field(default=None, ge=-50, le=50)
    timestamp: datetime | None = None


class LecturaResponse(LecturaBase):
    """Representación pública de lectura."""

    id: int
    timestamp: datetime

    model_config = {"from_attributes": True}
