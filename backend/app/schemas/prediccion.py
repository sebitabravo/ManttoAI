"""Schemas de predicción."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

ClasificacionPrediccion = Literal[
    "normal",
    "alerta",
    "falla",
    "advertencia",
    "critico",
]


class PrediccionCreate(BaseModel):
    """Payload para persistir una predicción manual o importada."""

    equipo_id: int
    clasificacion: ClasificacionPrediccion
    probabilidad: float
    modelo_version: str = "rf-mvp"


class PrediccionUpdate(BaseModel):
    """Payload para actualizar una predicción existente."""

    clasificacion: ClasificacionPrediccion | None = None
    probabilidad: float | None = None
    modelo_version: str | None = None


class PrediccionResponse(BaseModel):
    """Representación pública de una predicción."""

    id: int
    equipo_id: int
    clasificacion: ClasificacionPrediccion
    probabilidad: float
    modelo_version: str
    created_at: datetime

    model_config = {"from_attributes": True}
