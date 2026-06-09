"""Esquemas para el servicio de notificaciones Twilio."""

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Representa el resultado de un intento de envio via Twilio."""

    sent: bool = Field(..., description="Indica si la notificacion fue enviada exitosamente")
    channel: str = Field(..., description="Canal usado: whatsapp, sms o fallback")
    message: str = Field(..., description="Cuerpo del mensaje")
    to_number: str = Field(..., description="Numero destino enmascarado")
    error: str | None = Field(None, description="Mensaje de error en caso de falla")
    sid: str | None = Field(None, description="Twilio SID del mensaje enviado")
