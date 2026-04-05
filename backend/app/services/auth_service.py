"""Servicios relacionados a autenticación."""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.schemas.usuario import Token, UsuarioCreate, UsuarioResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    """Genera un hash seguro para una contraseña."""

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    """Crea un token JWT básico para el usuario."""

    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(hours=4)}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def register_user(payload: UsuarioCreate) -> UsuarioResponse:
    """Construye una respuesta de usuario demo para el scaffold."""

    return UsuarioResponse(
        id=1, nombre=payload.nombre, email=payload.email, rol=payload.rol
    )


def login_user(email: str) -> Token:
    """Retorna un token JWT para el email recibido."""

    return Token(access_token=create_access_token(email))
