"""Schemas de equipos."""

from typing import Literal
import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Any


EstadoEquipo = Literal[
    "operativo",
    "monitoreo",
    "detenido",
    "mantenimiento",
    "fuera_servicio",
]


def validate_mac_address(v: str | None) -> str | None:
    if v is None:
        return v
    if not re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", v):
        raise ValueError("Formato de MAC address inválido")
    return v


class EquipoBase(BaseModel):
    """Campos base de un equipo."""

    nombre: str
    ubicacion: str = "Laboratorio"
    tipo: str = "Motor"
    descripcion: str = "Equipo monitoreado por ManttoAI"
    estado: EstadoEquipo = "operativo"
    mac_address: str | None = Field(default=None, max_length=17)

    @field_validator("mac_address", mode="before")
    def validate_mac(cls, v):
        return validate_mac_address(v)


class EquipoCreate(EquipoBase):
    """Payload para crear equipo."""


class EquipoUpdate(BaseModel):
    """Payload para actualizar equipo."""

    nombre: str | None = None
    ubicacion: str | None = None
    tipo: str | None = None
    descripcion: str | None = None
    estado: EstadoEquipo | None = None
    mac_address: str | None = Field(default=None, max_length=17)

    @field_validator("mac_address", mode="before")
    def validate_mac(cls, v):
        return validate_mac_address(v)


class EquipoResponse(EquipoBase):
    """Representación pública de un equipo."""

    id: int
    created_at: datetime | None = None

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
    mac_address: str | None = Field(default=None, max_length=17)
    temperatura_max: float = 80.0
    vibracion_max: float = 0.5

    @field_validator("mac_address", mode="before")
    def validate_mac(cls, v):
        return validate_mac_address(v)


class EquipoFullSetupResponse(BaseModel):
    """Response con equipo y umbrales creados."""

    equipo: EquipoResponse
    umbral_temperatura_id: int
    created_at: datetime | None = None
    umbral_vibracion_id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AutoRegisterRequest(BaseModel):
    """Payload recibido desde el dispositivo durante el provisioning.

    El token es un JWT firmado por el backend con propósito 'provision'.
    """

    mac_address: str | None = Field(default=None, max_length=17)
    token: str

    @field_validator("mac_address", mode="before")
    def validate_mac(cls, v):
        return validate_mac_address(v)
