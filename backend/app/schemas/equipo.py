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


class UmbralCreateMinimal(BaseModel):
    """Schema mínimo para crear umbral en full-setup."""

    variable: str
    valor_min: float
    valor_max: float


class EquipoFullSetupRequest(BaseModel):
    """Request para crear equipo con umbrales en una sola transacción."""

    nombre: str
    ubicacion: str | None = None
    tipo: str | None = None
    descripcion: str | None = None
    temperatura_max: float = 80.0
    vibracion_max: float = 0.5


class EquipoFullSetupResponse(BaseModel):
    """Response con equipo y umbrales creados."""

    equipo: EquipoResponse
    umbral_temperatura_id: int
    umbral_vibracion_id: int

    model_config = {"from_attributes": True}
