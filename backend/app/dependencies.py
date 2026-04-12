"""Dependencias reutilizables de FastAPI."""

from collections.abc import Callable, Generator
from datetime import datetime, timezone

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models.api_key import APIKey
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
settings = get_settings()
JWT_ALGORITHM = "HS256"


def get_db() -> Generator[Session, None, None]:
    """Entrega una sesión de base de datos por request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _to_utc_epoch_seconds(value: datetime) -> float:
    """Convierte datetime a epoch UTC con precisión de segundos."""

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc).timestamp()

    return value.astimezone(timezone.utc).timestamp()


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

    # Soporte explícito para contextos sin Depends(oauth2_scheme),
    # por ejemplo middleware de auditoría ejecutado en threadpool.
    if not resolved_token:
        authorization_header = request.headers.get("Authorization", "")
        if authorization_header.lower().startswith("bearer "):
            bearer_token = authorization_header.split(" ", 1)[1].strip()
            if bearer_token:
                resolved_token = bearer_token
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

    token_iat_raw = payload.get("iat")
    try:
        token_iat = float(token_iat_raw)
    except (TypeError, ValueError):
        token_iat = None

    if usuario.password_changed_at is not None:
        password_changed_at = _to_utc_epoch_seconds(usuario.password_changed_at)
        if token_iat is None or token_iat < password_changed_at:
            raise credentials_exception

    return usuario


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator factory para requerir roles específicos.

    Roles válidos: "admin", "tecnico", "visualizador"

    Ejemplo:
        @router.get("", dependencies=[Depends(require_role("admin", "tecnico"))])
        def get_equipos(...):
            ...
    """

    async def role_checker(
        request: Request,
        current_user: Usuario = Depends(get_current_user),
    ) -> Usuario:
        """Verifica que el usuario tenga uno de los roles permitidos."""

        user_role = current_user.rol.lower() if current_user.rol else "visualizador"

        if user_role not in [role.lower() for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}",
            )

        # Exponer rol/usuario en request.state para limit_by_role.
        request.state.manttoai_user_role = user_role
        request.state.manttoai_user_id = current_user.id

        return current_user

    return role_checker


def get_api_key_user(
    api_key: str | None = Depends(api_key_header),
    db: Session = Depends(get_db),
) -> APIKey | None:
    """
    Valida una API Key y retorna el objeto APIKey si es válida.

    Se usa para autenticar dispositivos IoT (ESP32) vía MQTT o HTTP.
    """

    if not api_key:
        return None

    key_suffix = api_key[-8:] if len(api_key) >= 8 else api_key
    candidates = db.scalars(
        select(APIKey).where(
            APIKey.key_prefix == key_suffix,
            APIKey.is_active.is_(True),
        )
    ).all()

    for api_key_obj in candidates:
        try:
            if not bcrypt.checkpw(
                api_key.encode("utf-8"), api_key_obj.key_hash.encode("utf-8")
            ):
                continue

            api_key_obj.last_used_at = datetime.utcnow()
            db.commit()
            return api_key_obj
        except Exception:
            continue

    return None
