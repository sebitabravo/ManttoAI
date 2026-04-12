"""Tests para el servicio de API Keys."""

import pytest
from sqlalchemy.orm import Session

from app.models.api_key import APIKey
from app.models.usuario import Usuario
from app.services.api_key_service import (
    create_api_key,
    list_api_keys,
    revoke_api_key,
    validate_api_key,
)


def test_create_api_key(db: Session, admin_user: Usuario):
    """Test de creación de API key."""

    api_key, plain_key = create_api_key(
        db, device_id="esp32_001", created_by_id=admin_user.id
    )

    assert api_key.id is not None
    assert api_key.device_id == "esp32_001"
    assert api_key.is_active is True
    assert api_key.key_prefix == plain_key[-8:]
    assert plain_key.startswith("mttk_")

    # Verificar que se guardó en DB
    db_api_key = db.get(APIKey, api_key.id)
    assert db_api_key is not None
    assert db_api_key.device_id == "esp32_001"


def test_create_api_key_duplicate_device(db: Session, admin_user: Usuario):
    """Test que no permite crear API key para device_id duplicado."""

    create_api_key(db, device_id="esp32_001", created_by_id=admin_user.id)

    with pytest.raises(ValueError, match="Ya existe una API Key"):
        create_api_key(db, device_id="esp32_001", created_by_id=admin_user.id)


def test_list_api_keys(db: Session, admin_user: Usuario):
    """Test de listado de API keys."""

    # Crear varias API keys
    create_api_key(db, device_id="esp32_001", created_by_id=admin_user.id)
    create_api_key(db, device_id="esp32_002", created_by_id=admin_user.id)

    # Listar todas activas
    api_keys = list_api_keys(db, include_inactive=False)
    assert len(api_keys) == 2

    # Listar todas (incluyendo inactivas)
    all_keys = list_api_keys(db, include_inactive=True)
    assert len(all_keys) >= 2


def test_revoke_api_key(db: Session, admin_user: Usuario):
    """Test de revocación de API key."""

    api_key, _ = create_api_key(db, device_id="esp32_001", created_by_id=admin_user.id)

    # Revocar
    revoked_key = revoke_api_key(db, api_key.id)

    assert revoked_key.is_active is False
    assert revoked_key.revoked_at is not None

    # Verificar en DB
    db.refresh(revoked_key)
    assert revoked_key.is_active is False


def test_validate_api_key(db: Session, admin_user: Usuario):
    """Test de validación de API key."""

    api_key, plain_key = create_api_key(
        db, device_id="esp32_001", created_by_id=admin_user.id
    )

    # Validar key correcta
    validated = validate_api_key(db, plain_key)
    assert validated is not None
    assert validated.id == api_key.id
    assert validated.device_id == "esp32_001"

    # Validar key incorrecta
    invalid = validate_api_key(db, "mttk_wrong_key")
    assert invalid is None

    # Validar key revocada
    revoke_api_key(db, api_key.id)
    revoked = validate_api_key(db, plain_key)
    assert revoked is None
