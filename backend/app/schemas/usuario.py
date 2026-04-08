"""Schemas de usuario y autenticación."""

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
