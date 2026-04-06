"""Dependencias reutilizables de FastAPI."""

from collections.abc import Generator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
settings = get_settings()
JWT_ALGORITHM = "HS256"


def get_db() -> Generator[Session, None, None]:
    """Entrega una sesión de base de datos por request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Resuelve el usuario autenticado a partir del JWT recibido."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    resolved_token = token or request.cookies.get(settings.auth_cookie_name)
    if not resolved_token:
        raise credentials_exception

    is_cookie_auth = token is None and request.cookies.get(settings.auth_cookie_name)
    if is_cookie_auth and request.method.upper() not in {"GET", "HEAD", "OPTIONS"}:
        csrf_cookie = request.cookies.get(settings.auth_csrf_cookie_name)
        csrf_header = request.headers.get(settings.auth_csrf_header_name)
        if not csrf_cookie or csrf_cookie != csrf_header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token inválido o ausente",
            )

    try:
        payload = jwt.decode(
            resolved_token,
            settings.secret_key,
            algorithms=[JWT_ALGORITHM],
        )
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    usuario = db.scalars(select(Usuario).where(Usuario.email == subject)).first()
    if usuario is None:
        raise credentials_exception

    return usuario
