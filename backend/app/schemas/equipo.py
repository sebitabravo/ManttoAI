"""Schemas de equipos."""

from pydantic import BaseModel


class EquipoBase(BaseModel):
    """Campos base de un equipo."""

    nombre: str
    ubicacion: str = "Laboratorio"
    tipo: str = "Motor"
    estado: str = "operativo"


class EquipoCreate(EquipoBase):
    """Payload para crear equipo."""


class EquipoUpdate(BaseModel):
    """Payload para actualizar equipo."""

    nombre: str | None = None
    ubicacion: str | None = None
    tipo: str | None = None
    estado: str | None = None


class EquipoResponse(EquipoBase):
    """Representación pública de un equipo."""

    id: int

    model_config = {"from_attributes": True}
