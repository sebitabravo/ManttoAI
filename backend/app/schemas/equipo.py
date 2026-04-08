"""Schemas de equipos."""

from typing import Literal

from pydantic import BaseModel


EstadoEquipo = Literal[
    "operativo",
    "monitoreo",
    "detenido",
    "mantenimiento",
    "fuera_servicio",
]


class EquipoBase(BaseModel):
    """Campos base de un equipo."""

    nombre: str
    ubicacion: str = "Laboratorio"
    tipo: str = "Motor"
    descripcion: str = "Equipo monitoreado por ManttoAI"
    estado: EstadoEquipo = "operativo"


class EquipoCreate(EquipoBase):
    """Payload para crear equipo."""


class EquipoUpdate(BaseModel):
    """Payload para actualizar equipo."""

    nombre: str | None = None
    ubicacion: str | None = None
    tipo: str | None = None
    descripcion: str | None = None
    estado: EstadoEquipo | None = None


class EquipoResponse(EquipoBase):
    """Representación pública de un equipo."""

    id: int

    model_config = {"from_attributes": True}
