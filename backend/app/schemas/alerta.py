"""Schemas de alertas."""

from datetime import datetime

from pydantic import BaseModel


class AlertaResponse(BaseModel):
    """Representación pública de alerta."""

    id: int
    equipo_id: int
    tipo: str
    mensaje: str
    nivel: str
    email_enviado: bool
    leida: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertaUpdate(BaseModel):
    """Payload para marcar una alerta."""

    leida: bool = True
