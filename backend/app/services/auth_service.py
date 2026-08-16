"""Servicios relacionados a autenticación."""

import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException, status
import jwt
from jwt import InvalidTokenError as JWTError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.revoked_token import RevokedToken
from app.models.usuario import Usuario
from app.schemas.usuario import (
    Token,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioSelfRegister,
)
from app.services.tenant_scope import UNSCOPED, resolve_organization_id

settings = get_settings()
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 4


def get_user_by_email(db: Session, email: str) -> Usuario | None:
    """Obtiene un usuario persistido por su email."""

    return db.scalars(select(Usuario).where(Usuario.email == email)).first()


def hash_password(password: str) -> str:
    """Genera un hash bcrypt seguro para una contraseña."""

    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt."""

    plain_password_bytes = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except (AttributeError, TypeError, ValueError):
        # Cuentas anonimizadas o hashes corruptos deben fallar como credencial
        # inválida, nunca convertirse en un error 500 del endpoint de login.
        return False


def create_access_token(subject: str) -> str:
    """Crea un token JWT con JTI único para permitir revocación."""

    expire_at = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    issued_at = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": issued_at.timestamp(),
        "exp": int(expire_at.timestamp()),
        "jti": secrets.token_urlsafe(16),  # Identificador único para blacklist
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def revoke_access_token(db: Session, token: str) -> bool:
    """Persiste la revocación de un JWT hasta que expire naturalmente."""

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False},
        )
    except JWTError:
        return False

    jti = payload.get("jti")
    exp = payload.get("exp")
    if not isinstance(jti, str) or not jti or len(jti) > 64:
        return False

    try:
        expires_at = datetime.fromtimestamp(float(exp), tz=timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return False

    if expires_at <= datetime.now(timezone.utc):
        return False

    existing = db.scalar(select(RevokedToken).where(RevokedToken.jti == jti))
    if existing is not None:
        return True

    db.add(RevokedToken(jti=jti, expires_at=expires_at))
    try:
        db.commit()
    except IntegrityError:
        # Dos logouts concurrentes pueden competir por el índice único de jti.
        db.rollback()
        return (
            db.scalar(select(RevokedToken).where(RevokedToken.jti == jti)) is not None
        )
    except SQLAlchemyError:
        db.rollback()
        raise

    return True


def register_user(
    db: Session,
    payload: UsuarioCreate | UsuarioSelfRegister,
    organization_id: int | None | object = UNSCOPED,
) -> UsuarioResponse:
    """Registra un usuario y separa el rol público del flujo administrativo."""

    existing_user = get_user_by_email(db, payload.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ya registrado",
        )

    values = {
        "nombre": payload.nombre,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "rol": getattr(payload, "rol", "visualizador"),
    }
    resolved_id = resolve_organization_id(db, organization_id)
    if resolved_id is not UNSCOPED:
        values["organizacion_id"] = resolved_id

    usuario = Usuario(
        **values,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return UsuarioResponse.model_validate(usuario)


def authenticate_user(db: Session, email: str, password: str) -> Usuario:
    """Valida credenciales y retorna usuario persistido."""

    usuario = get_user_by_email(db, email)
    if (
        usuario is None
        or not usuario.is_active
        or not verify_password(password, usuario.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


def change_password(
    db: Session, user: Usuario, current_password: str, new_password: str
) -> dict:
    """Cambia la contraseña de un usuario autenticado."""

    if user.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta demo es de solo lectura",
        )

    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta",
        )

    user.password_hash = hash_password(new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Contraseña actualizada exitosamente"}


def login_user(db: Session, email: str, password: str) -> Token:
    """Retorna un token JWT para credenciales válidas."""

    usuario = authenticate_user(db, email=email, password=password)

    return Token(access_token=create_access_token(str(usuario.id)))
