"""Dependencias reutilizables de FastAPI."""

from collections.abc import Callable, Generator
from datetime import datetime, timezone
import logging

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError as JWTError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_redis_connection_kwargs, get_settings
from app.database import SessionLocal
from app.models.api_key import APIKey
from app.models.revoked_token import RevokedToken
from app.models.usuario import Usuario
from app.services.api_key_service import validate_api_key
from app.services.tenant_scope import UNSCOPED

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
settings = get_settings()
JWT_ALGORITHM = "HS256"
logger = logging.getLogger(__name__)
_api_prefix = settings.api_prefix.strip().strip("/")
API_ROUTE_PREFIX = f"/{_api_prefix}" if _api_prefix else "/api/v1"
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{API_ROUTE_PREFIX}/auth/login", auto_error=False
)

# Redis es una caché opcional: la fuente autoritativa de revocación permanece
# en MySQL. Se conserva un cliente compartido para reutilizar su pool de
# conexiones y no crear un objeto Redis nuevo en cada request autenticado.
_revocation_redis_client = None
_revocation_redis_config: tuple[str, str] | None = None


def get_revocation_redis_client():
    """Retorna un cliente Redis compartido para la caché de revocación."""

    global _revocation_redis_client, _revocation_redis_config

    redis_url = settings.redis_url.strip()
    redis_password = settings.redis_password.strip()
    config_key = (redis_url, redis_password)

    if not redis_url:
        _revocation_redis_client = None
        _revocation_redis_config = None
        return None

    if _revocation_redis_client is not None and _revocation_redis_config == config_key:
        return _revocation_redis_client

    try:
        import redis as redis_lib

        _revocation_redis_client = redis_lib.from_url(
            redis_url,
            socket_connect_timeout=1,
            **get_redis_connection_kwargs(settings),
        )
        _revocation_redis_config = config_key
        return _revocation_redis_client
    except ImportError:
        logger.warning("Redis no disponible para verificar tokens revocados.")
    except Exception as exc:
        logger.warning("No se pudo preparar la caché Redis de revocación: %s", exc)

    _revocation_redis_client = None
    _revocation_redis_config = None
    return None


def get_db(request: Request) -> Generator[Session, None, None]:
    """Entrega una sesión de base de datos por request."""

    db = SessionLocal()
    # La dependencia de autenticación reutiliza esta misma sesión y escribe el
    # tenant validado después de resolver el JWT. Los servicios consumen db.info
    # para no depender de un header controlable por el cliente.
    db.info["organizacion_id"] = UNSCOPED
    request.state.db_session = db
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

    # La base es la fuente persistente de revocación; Redis queda como caché
    # opcional para mantener compatibilidad con el despliegue Compose.
    jti = payload.get("jti")
    if isinstance(jti, str) and jti:
        try:
            if (
                db.scalar(select(RevokedToken.id).where(RevokedToken.jti == jti))
                is not None
            ):
                raise credentials_exception
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            logger.exception("No se pudo verificar la revocación persistente del JWT")
            raise credentials_exception from exc

    if jti and settings.redis_url.strip():
        redis_client = get_revocation_redis_client()
        if redis_client:
            try:
                if redis_client.exists(f"blacklist:{jti}"):
                    raise credentials_exception
            except HTTPException:
                raise
            except Exception as exc:
                logger.error("Error al verificar blacklist de Redis: %s", exc)
                pass  # Degradación elegante si hay un error de comunicación con Redis

    try:
        user_id = int(subject)
    except (ValueError, TypeError):
        raise credentials_exception

    usuario = db.scalars(select(Usuario).where(Usuario.id == user_id)).first()
    if usuario is None or not usuario.is_active:
        raise credentials_exception

    db.info["organizacion_id"] = usuario.organizacion_id
    request.state.authenticated_organization_id = usuario.organizacion_id

    # Tenant isolation: si el middleware detectó X-Tenant-ID, verificar membresía
    tenant_id = getattr(request.state, "tenant_id", None)
    if tenant_id is not None:
        if usuario.organizacion_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: no pertenece al tenant especificado",
            )

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

    return validate_api_key(db, api_key)
