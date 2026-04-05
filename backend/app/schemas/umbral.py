"""Schemas de umbrales."""

from pydantic import BaseModel


class UmbralBase(BaseModel):
    """Campos base de umbral."""

    equipo_id: int
    variable: str
    valor_min: float
    valor_max: float


class UmbralCreate(UmbralBase):
    """Payload para crear umbral."""


class UmbralUpdate(BaseModel):
    """Payload para actualizar umbral."""

    valor_min: float | None = None
    valor_max: float | None = None


class UmbralResponse(UmbralBase):
    """Representación pública de umbral."""

    id: int

    model_config = {"from_attributes": True}
