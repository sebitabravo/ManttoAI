"""Schemas de predicción."""

from datetime import datetime

from pydantic import BaseModel


class PrediccionResponse(BaseModel):
    """Representación pública de una predicción."""

    id: int
    equipo_id: int
    clasificacion: str
    probabilidad: float
    modelo_version: str
    created_at: datetime

    model_config = {"from_attributes": True}
