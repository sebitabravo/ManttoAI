"""Schemas de usuario y autenticación."""

from pydantic import BaseModel, EmailStr


class UsuarioBase(BaseModel):
    """Campos base de usuario."""

    nombre: str
    email: EmailStr
    rol: str = "visualizador"


class UsuarioCreate(UsuarioBase):
    """Payload para registrar usuario."""

    password: str


class UsuarioResponse(UsuarioBase):
    """Representación pública de usuario."""

    id: int

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Payload para autenticación."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Token JWT simplificado."""

    access_token: str
    token_type: str = "bearer"
