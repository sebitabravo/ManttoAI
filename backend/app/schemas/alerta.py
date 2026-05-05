"""Schemas de alertas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

NivelAlerta = Literal["bajo", "medio", "alto", "critico"]


class AlertaCreate(BaseModel):
    """Payload para crear una alerta manualmente."""

    equipo_id: int
    tipo: str
    mensaje: str
    nivel: NivelAlerta = "medio"
    email_enviado: bool = False
    leida: bool = False


class AlertaResponse(BaseModel):
    """Representación pública de alerta."""

    id: int
    equipo_id: int
    tipo: str
    mensaje: str
    nivel: NivelAlerta
    email_enviado: bool
    leida: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertaUpdate(BaseModel):
    """Payload para marcar una alerta."""

    leida: bool = True


class AlertaMarkReadResponse(BaseModel):
    """Respuesta simple al marcar una alerta como leída."""

    id: int
    leida: bool


class AlertaCountResponse(BaseModel):
    """Respuesta de conteo de alertas para widgets rápidos."""

    total: int
    no_leidas: int
