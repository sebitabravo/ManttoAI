"""Endpoints de autenticación."""

import secrets

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.dependencies import get_current_user
from app.dependencies import get_db
from app.schemas.usuario import LoginRequest, Token, UsuarioCreate, UsuarioResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post(
    "/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
def register(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    """Registra un usuario persistido."""

    return register_user(db, payload)


@router.post("/login", response_model=Token)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> Token:
    """Retorna un token JWT para credenciales válidas."""

    token = login_user(db, payload.email, payload.password)
    csrf_token = secrets.token_urlsafe(32)
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token.access_token,
        httponly=True,
        samesite="lax",
        secure=settings.app_env.strip().lower()
        in {"staging", "stage", "production", "prod"},
        max_age=60 * 60 * 4,
    )
    response.set_cookie(
        key=settings.auth_csrf_cookie_name,
        value=csrf_token,
        httponly=False,
        samesite="lax",
        secure=settings.app_env.strip().lower()
        in {"staging", "stage", "production", "prod"},
        max_age=60 * 60 * 4,
    )
    return token


@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user=Depends(get_current_user)) -> UsuarioResponse:
    """Retorna el usuario autenticado usando header o cookie."""

    return UsuarioResponse.model_validate(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    """Limpia la cookie de autenticación para clientes web."""

    response.delete_cookie(
        key=settings.auth_cookie_name,
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(
        key=settings.auth_csrf_cookie_name,
        httponly=False,
        samesite="lax",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
