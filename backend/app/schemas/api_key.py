"""Schemas Pydantic para API Keys."""

from datetime import datetime

from pydantic import BaseModel, Field


class APIKeyCreate(BaseModel):
    """Schema para crear una nueva API Key."""

    device_id: str = Field(..., description="ID del dispositivo IoT")


class APIKeyResponse(BaseModel):
    """Schema para respuesta de API Key."""

    id: int
    key_prefix: str
    device_id: str
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None = None
    revoked_at: datetime | None = None

    class Config:
        from_attributes = True


class APIKeyDetailResponse(APIKeyResponse):
    """Schema para detalle de API Key (incluye la key completa al crear)."""

    key: str = Field(..., description="API Key completa (solo se muestra una vez)")


class APIKeyUpdate(BaseModel):
    """Schema para actualizar una API Key."""

    is_active: bool | None = None
