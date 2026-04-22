"""Schemas de usuario y autenticación."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


def _normalize_and_validate_email(value: str) -> str:
    """Normaliza email y valida formato básico compatible con dominios .local."""

    normalized = value.strip().lower()
    local_part, separator, domain_part = normalized.partition("@")

    if separator != "@" or not local_part or not domain_part:
        raise ValueError("email inválido")

    if "." not in domain_part:
        raise ValueError("email inválido")

    return normalized


class UsuarioBase(BaseModel):
    """Campos base de usuario."""

    nombre: str
    email: str
    rol: Literal["admin", "tecnico", "visualizador"] = "visualizador"

    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        """Valida formato de email para registro de usuario."""

        return _normalize_and_validate_email(value)


class UsuarioCreate(UsuarioBase):
    """Payload para registrar usuario."""

    password: str

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        """Valida longitud mínima de contraseña para registro."""

        if len(value) < 8:
            raise ValueError("password debe tener al menos 8 caracteres")

        return value


class UsuarioResponse(UsuarioBase):
    """Representación pública de usuario."""

    id: int
    created_at: datetime | None = None
    telefono: str | None = None
    avatar: str | None = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Payload para autenticación."""

    email: str
    password: str

    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        """Valida formato de email para inicio de sesión."""

        return _normalize_and_validate_email(value)


class Token(BaseModel):
    """Token JWT simplificado."""

    access_token: str
    token_type: str = "bearer"


class UsuarioUpdate(BaseModel):
    """Payload para actualizar usuario (desde admin)."""

    nombre: str | None = None
    email: str | None = None
    telefono: str | None = None
    rol: Literal["admin", "tecnico", "visualizador"] | None = None
    is_active: bool | None = None

    @field_validator("email")
    def validate_email(cls, value: str | None) -> str | None:
        """Valida formato de email si se proporciona."""

        if value is None:
            return None
        return _normalize_and_validate_email(value)


class ChangePasswordRequest(BaseModel):
    """Payload para cambio de contraseña."""

    current_password: str
    new_password: str

    @field_validator("new_password")
    def validate_new_password(cls, value: str) -> str:
        """Valida longitud mínima de la nueva contraseña."""

        if len(value) < 8:
            raise ValueError("password debe tener al menos 8 caracteres")

        return value


class UsuarioListResponse(BaseModel):
    """Respuesta para lista de usuarios."""

    usuarios: list[UsuarioResponse]
    total: int
    page: int
    per_page: int


class ProfileUpdate(BaseModel):
    """Payload para que el usuario edite su propio perfil (solo nombre y avatar).

    Teléfono no es editable - se configura desde admin.
    """

    nombre: str | None = None
    avatar: str | None = None

    @field_validator("nombre")
    def validate_nombre(cls, value: str | None) -> str | None:
        if value is not None and len(value.strip()) < 2:
            raise ValueError("nombre debe tener al menos 2 caracteres")
        return value.strip() if value else value


class ProfileResponse(BaseModel):
    """Respuesta del perfil del usuario autenticado."""

    id: int
    created_at: datetime | None = None
    nombre: str
    email: str
    telefono: str | None = None
    avatar: str | None = None
    rol: str

    model_config = {"from_attributes": True}
