"""Schemas de mantenciones."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

TipoMantencion = Literal["preventiva", "correctiva", "predictiva", "emergencia"]
EstadoMantencion = Literal[
    "programada",
    "en_proceso",
    "ejecutada",
    "completada",
    "cancelada",
]


class MantencionBase(BaseModel):
    """Campos base de mantención."""

    equipo_id: int
    tipo: TipoMantencion = "preventiva"
    descripcion: str = "Pendiente de definir"
    fecha_programada: datetime | None = None
    fecha_ejecucion: datetime | None = None
    estado: EstadoMantencion = "programada"


class MantencionCreate(MantencionBase):
    """Payload para crear mantención."""


class MantencionUpdate(BaseModel):
    """Payload para actualizar mantención."""

    tipo: TipoMantencion | None = None
    descripcion: str | None = None
    fecha_programada: datetime | None = None
    fecha_ejecucion: datetime | None = None
    estado: EstadoMantencion | None = None


class MantencionResponse(MantencionBase):
    """Representación pública de mantención."""

    id: int

    model_config = {"from_attributes": True}
