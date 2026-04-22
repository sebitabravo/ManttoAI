"""Schemas para el Asistente de Mantenimiento con IA."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ChatMessageRequest(BaseModel):
    """Mensaje entrante del usuario."""

    mensaje: str = Field(
        ..., min_length=2, max_length=500, description="Pregunta del técnico"
    )
    historial: list = Field(default=[], description="Historial de la conversación")


class ChatMessageResponse(BaseModel):
    """Respuesta del asistente."""

    respuesta: str
    fuente: str = Field(default="reglas", description="'reglas' o 'ollama'")


class UsuarioChatInfo(BaseModel):
    """Información del usuario que hizo la pregunta."""

    id: int
    nombre: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryResponse(BaseModel):
    """Esquema de respuesta para el historial de chat (Admin)."""

    id: int
    mensaje_usuario: str
    respuesta_ia: str
    fuente: str
    fecha_creacion: datetime
    usuario: UsuarioChatInfo

    model_config = ConfigDict(from_attributes=True)
