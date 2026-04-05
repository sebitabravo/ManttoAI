"""Schemas de mantenciones."""

from pydantic import BaseModel


class MantencionBase(BaseModel):
    """Campos base de mantención."""

    equipo_id: int
    tipo: str = "preventiva"
    descripcion: str = "Pendiente de definir"
    estado: str = "programada"


class MantencionCreate(MantencionBase):
    """Payload para crear mantención."""


class MantencionUpdate(BaseModel):
    """Payload para actualizar mantención."""

    tipo: str | None = None
    descripcion: str | None = None
    estado: str | None = None


class MantencionResponse(MantencionBase):
    """Representación pública de mantención."""

    id: int

    model_config = {"from_attributes": True}
