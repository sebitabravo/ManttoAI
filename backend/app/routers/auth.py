"""Endpoints de autenticación."""

import logging
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
import jwt
from jwt import InvalidTokenError as JWTError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import NON_DEV_ENVS, get_settings
from app.dependencies import (
    get_current_user,
    get_db,
    get_revocation_redis_client,
)
from app.middleware.rate_limit import limiter
from app.schemas.usuario import (
    ChangePasswordRequest,
    LoginRequest,
    ProfileUpdate,
    Token,
    UsuarioResponse,
    UsuarioSelfRegister,
)
from app.services.auth_service import (
    change_password,
    login_user,
    register_user,
    revoke_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post(
    "/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
def register(
    payload: UsuarioSelfRegister,
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
        secure=settings.app_env.strip().lower() in NON_DEV_ENVS,
        max_age=60 * 60 * 4,
    )
    response.set_cookie(
        key=settings.auth_csrf_cookie_name,
        value=csrf_token,
        httponly=False,
        samesite="lax",
        secure=settings.app_env.strip().lower() in NON_DEV_ENVS,
        max_age=60 * 60 * 4,
    )
    return token


@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user=Depends(get_current_user)) -> UsuarioResponse:
    """Retorna el usuario autenticado usando header o cookie."""

    return UsuarioResponse.model_validate(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> Response:
    """Limpia cookies y revoca el JWT de forma persistente."""

    token = (
        request.cookies.get(settings.auth_cookie_name)
        or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    )
    if token:
        try:
            revoke_access_token(db, token)
        except SQLAlchemyError as exc:
            logger.exception("No se pudo persistir la revocación del JWT")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo revocar la sesión",
            ) from exc

        # Redis se mantiene como caché opcional para despliegues que ya lo usan.
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
                redis_client = get_revocation_redis_client()
                if redis_client is not None:
                    ttl = max(int(exp - datetime.now(timezone.utc).timestamp()), 1)
                    redis_client.setex(f"blacklist:{jti}", ttl, "1")
        except JWTError:
            pass  # Un token inválido no necesita entrar a la blacklist.
        except Exception as exc:
            logger.warning("No se pudo actualizar la blacklist Redis: %s", exc)

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

    if getattr(usuario, "is_demo", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta demo es de solo lectura",
        )

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
