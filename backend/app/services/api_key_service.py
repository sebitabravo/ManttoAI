"""Servicio de negocio para gestión de API Keys."""

import logging
import secrets
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.api_key import APIKey

logger = logging.getLogger(__name__)


def generate_api_key() -> str:
    """Genera una nueva API Key segura."""

    return f"mttk_{secrets.token_urlsafe(32)}"


def hash_api_key(plain_key: str) -> str:
    """Genera hash bcrypt para una API key."""

    return bcrypt.hashpw(plain_key.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode(
        "utf-8"
    )


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verifica API key plaintext contra hash almacenado."""

    try:
        return bcrypt.checkpw(plain_key.encode("utf-8"), hashed_key.encode("utf-8"))
    except ValueError:
        return False


def create_api_key(
    db: Session,
    device_id: str,
    created_by_id: int,
) -> tuple[APIKey, str]:
    """
    Crea una nueva API Key para un dispositivo.

    Retorna:
        tuple: (APIKey object, plain key - SOLO se muestra una vez)
    """

    # Verificar que device_id no exista
    existing = db.scalars(select(APIKey).where(APIKey.device_id == device_id)).first()
    if existing:
        raise ValueError(f"Ya existe una API Key para el dispositivo {device_id}")

    # Generar key y hash
    plain_key = generate_api_key()
    key_hash = hash_api_key(plain_key)
    key_prefix = plain_key[-8:]  # Últimos 8 caracteres para UI

    # Crear API key
    api_key = APIKey(
        key_hash=key_hash,
        key_prefix=key_prefix,
        device_id=device_id,
        created_by_id=created_by_id,
        is_active=True,
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return api_key, plain_key


def get_api_key_by_id(db: Session, api_key_id: int) -> APIKey | None:
    """Retorna una API Key por ID."""

    return db.get(APIKey, api_key_id)


def list_api_keys(
    db: Session,
    include_inactive: bool = False,
    device_id: str | None = None,
) -> list[APIKey]:
    """Lista todas las API Keys con filtros opcionales."""

    query = select(APIKey)

    if not include_inactive:
        query = query.where(APIKey.is_active.is_(True))

    if device_id:
        query = query.where(APIKey.device_id == device_id)

    return list(db.scalars(query.order_by(APIKey.created_at.desc())).all())


def revoke_api_key(db: Session, api_key_id: int) -> APIKey:
    """Revoca (desactiva) una API Key."""

    api_key = db.get(APIKey, api_key_id)
    if not api_key:
        raise ValueError(f"API Key con ID {api_key_id} no encontrada")

    api_key.is_active = False
    api_key.revoked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(api_key)

    return api_key


def validate_api_key(db: Session, plain_key: str) -> APIKey | None:
    """
    Valida una API Key y retorna el objeto si es válida.

    Usado por el suscriptor MQTT para autenticar dispositivos.
    """

    key_suffix = plain_key[-8:] if len(plain_key) >= 8 else plain_key
    candidates = db.scalars(
        select(APIKey).where(
            APIKey.key_prefix == key_suffix,
            APIKey.is_active.is_(True),
        )
    ).all()

    for api_key in candidates:
        try:
            is_valid = verify_api_key(plain_key, api_key.key_hash)
        except (AttributeError, TypeError, ValueError) as exc:
            logger.warning(
                "No se pudo validar candidate API key id=%s: %s: %s",
                getattr(api_key, "id", "n/a"),
                type(exc).__name__,
                str(exc),
            )
            continue

        if not is_valid:
            continue

        api_key.last_used_at = datetime.now(timezone.utc)
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "No se pudo persistir last_used_at para API key id=%s",
                api_key.id,
            )
        return api_key

    return None
