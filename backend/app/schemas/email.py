"""Esquemas para el servicio de email."""

from pydantic import BaseModel, Field


class EmailResponse(BaseModel):
    """Representa el resultado de un intento de envío de correo."""

    sent: bool = Field(..., description="Indica si el correo fue enviado exitosamente")
    subject: str = Field(..., description="Asunto del correo")
    message: str = Field(..., description="Cuerpo del mensaje")
    error: str | None = Field(None, description="Mensaje de error en caso de falla")
