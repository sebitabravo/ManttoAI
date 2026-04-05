"""Servicios relacionados a autenticación."""

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.usuario import Usuario
from app.schemas.usuario import Token, UsuarioCreate, UsuarioResponse

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
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


def create_access_token(subject: str) -> str:
    """Crea un token JWT básico para el usuario."""

    expire_at = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    issued_at = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(issued_at.timestamp()),
        "exp": int(expire_at.timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def register_user(db: Session, payload: UsuarioCreate) -> UsuarioResponse:
    """Registra y persiste un usuario nuevo con contraseña hasheada."""

    existing_user = get_user_by_email(db, payload.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email ya registrado",
        )

    usuario = Usuario(
        nombre=payload.nombre,
        email=payload.email,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return UsuarioResponse.model_validate(usuario)


def authenticate_user(db: Session, email: str, password: str) -> Usuario:
    """Valida credenciales y retorna usuario persistido."""

    usuario = get_user_by_email(db, email)
    if usuario is None or not verify_password(password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


def login_user(db: Session, email: str, password: str) -> Token:
    """Retorna un token JWT para credenciales válidas."""

    usuario = authenticate_user(db, email=email, password=password)

    return Token(access_token=create_access_token(usuario.email))
