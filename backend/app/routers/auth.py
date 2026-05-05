"""Endpoints de autenticación."""

import logging
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.dependencies import get_current_user
from app.dependencies import get_db
from app.middleware.rate_limit import limiter
from app.schemas.usuario import (
    ChangePasswordRequest,
    LoginRequest,
    ProfileUpdate,
    Token,
    UsuarioCreate,
    UsuarioResponse,
)
from app.services.auth_service import change_password, login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post(
    "/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
def register(
    payload: UsuarioCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    """Registra un usuario persistido."""

    return register_user(db, payload)


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
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
def logout(request: Request, response: Response) -> Response:
    """Limpia cookie de autenticación y revoca el JWT en blacklist Redis."""

    # Intentar revocar el token actual en Redis
    token = (
        request.cookies.get(settings.auth_cookie_name)
        or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    )
    if token:
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=["HS256"],
                options={"verify_exp": False},
            )
            jti = payload.get("jti", "")
            exp = payload.get("exp", 0)
            if jti and exp:
                try:
                    import redis as redis_lib
                except ImportError:
                    redis_lib = None
                if redis_lib is not None:
                    ttl = max(int(exp - datetime.now(timezone.utc).timestamp()), 1)
                    r = redis_lib.Redis(
                        host=settings.redis_host,
                        port=settings.redis_port,
                        password=settings.redis_password or None,
                        socket_connect_timeout=1,
                    )
                    r.setex(f"blacklist:{jti}", ttl, "1")
        except Exception:
            pass  # Degradación elegante: el token expira naturalmente

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


@router.post("/change-password")
@limiter.limit("5/minute")
def change_password_endpoint(
    payload: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    """Cambia la contraseña del usuario autenticado."""

    return change_password(
        db=db,
        user=current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )


@router.put("/profile", response_model=UsuarioResponse)
def update_profile(
    payload: ProfileUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> UsuarioResponse:
    """Actualiza el perfil del usuario autenticado (solo nombre y avatar).

    Nota: teléfono no es editable por el usuario - se configura desde admin.
    Email no es editable por el usuario (para evitar problemas de verificación).
    """

    # Usar el usuario proporcionado por la dependencia (ya está autenticado y verificado)
    # No necesitamos recargar - current_user es el usuario correcto
    usuario = current_user

    # Solo nombre y avatar son editables por el usuario
    if payload.nombre is not None:
        usuario.nombre = payload.nombre

    if payload.avatar is not None:
        usuario.avatar = payload.avatar

    # Teléfono NO se actualiza desde aquí - solo desde admin

    try:
        db.commit()
        db.refresh(usuario)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="No se pudo actualizar el perfil"
        ) from e

    return UsuarioResponse.model_validate(usuario)
