"""Endpoints de autenticación."""

from fastapi import APIRouter

from app.schemas.usuario import LoginRequest, Token, UsuarioCreate, UsuarioResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UsuarioResponse)
def register(payload: UsuarioCreate) -> UsuarioResponse:
    """Registra un usuario demo."""

    return register_user(payload)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest) -> Token:
    """Retorna un token demo para el usuario."""

    return login_user(payload.email)
