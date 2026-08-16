"""Tests de autenticación."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
import jwt
from sqlalchemy import select

from app.config import get_settings
from app.models.revoked_token import RevokedToken
from app.models.usuario import Usuario
from app.routers.auth import update_profile
from app.schemas.usuario import ProfileUpdate
from app.services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
)


def test_register_endpoint_persists_user_with_hashed_password(unauthenticated_client):
    """Valida que registro persista usuario real con contraseña hasheada."""

    payload = {
        "nombre": "Sebastián",
        "email": "sebastian@example.com",
        "password": "Test1234!",
        "rol": "admin",
    }

    response = unauthenticated_client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]

    session_local = unauthenticated_client.app.state.testing_session_local
    with session_local() as db:
        usuario = db.scalars(
            select(Usuario).where(Usuario.email == payload["email"])
        ).first()

    assert usuario is not None
    assert usuario.rol == "visualizador"
    assert usuario.password_hash != payload["password"]
    assert verify_password(payload["password"], usuario.password_hash)


def test_login_endpoint_returns_token_for_valid_credentials(unauthenticated_client):
    """Valida que login retorne token cuando credenciales son correctas."""

    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_endpoint_sets_http_only_cookie_for_valid_credentials(
    unauthenticated_client,
):
    """Valida que login además entregue cookie HttpOnly para auth web."""

    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )

    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert "manttoai_token=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "manttoai_csrf=" in set_cookie


def test_auth_me_returns_current_user_from_cookie(unauthenticated_client):
    """Valida restauración de sesión usando cookie HttpOnly."""

    login_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200

    response = unauthenticated_client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "admin@manttoai.local"


def test_protected_endpoint_accepts_http_only_cookie_authentication(
    unauthenticated_client,
):
    """Valida acceso autenticado aun sin header Authorization explícito."""

    login_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200

    response = unauthenticated_client.get("/api/v1/equipos")

    assert response.status_code == 200


def test_cookie_auth_requires_csrf_header_for_mutations(unauthenticated_client):
    """Valida protección CSRF cuando la sesión web usa cookie HttpOnly."""

    login_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200

    payload = {
        "nombre": "Equipo demo",
        "ubicacion": "Laboratorio",
        "tipo": "Motor",
        "estado": "operativo",
    }

    blocked_response = unauthenticated_client.post("/api/v1/equipos", json=payload)
    assert blocked_response.status_code == 403

    csrf_token = unauthenticated_client.cookies.get("manttoai_csrf")
    allowed_response = unauthenticated_client.post(
        "/api/v1/equipos",
        json=payload,
        headers={"X-CSRF-Token": csrf_token},
    )
    assert allowed_response.status_code == 201


def test_logout_endpoint_clears_auth_cookie(unauthenticated_client):
    """Valida cierre de sesión borrando cookie y bloqueando acceso posterior."""

    login_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200

    logout_response = unauthenticated_client.post("/api/v1/auth/logout")

    assert logout_response.status_code == 204
    assert "manttoai_token=" in logout_response.headers.get("set-cookie", "")

    protected_response = unauthenticated_client.get("/api/v1/equipos")
    assert protected_response.status_code == 401


def test_login_endpoint_rejects_invalid_credentials(unauthenticated_client):
    """Valida que login rechace credenciales inválidas."""

    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "incorrecta"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


def test_login_endpoint_rejects_inactive_user(unauthenticated_client):
    """Valida que un usuario desactivado no pueda autenticarse."""

    session_local = unauthenticated_client.app.state.testing_session_local
    with session_local() as db:
        usuario = db.scalars(
            select(Usuario).where(Usuario.email == "admin@manttoai.local")
        ).first()
        assert usuario is not None
        usuario.is_active = False
        db.commit()

    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


def test_login_endpoint_rejects_anonymized_user_without_server_error(
    unauthenticated_client,
):
    """Una cuenta anonimizada no debe romper el login con un hash inválido."""

    session_local = unauthenticated_client.app.state.testing_session_local
    with session_local() as db:
        usuario = db.scalars(
            select(Usuario).where(Usuario.email == "admin@manttoai.local")
        ).first()
        assert usuario is not None
        usuario.password_hash = "ELIMINADO"
        usuario.is_active = False
        db.commit()

    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


def test_protected_endpoint_rejects_inactive_user_token(unauthenticated_client):
    """Valida que un token de usuario inactivo no permita usar la API."""

    session_local = unauthenticated_client.app.state.testing_session_local
    with session_local() as db:
        usuario = db.scalars(
            select(Usuario).where(Usuario.email == "admin@manttoai.local")
        ).first()
        assert usuario is not None
        usuario.is_active = False
        db.commit()
        user_id = usuario.id

    token = create_access_token(str(user_id))
    response = unauthenticated_client.get(
        "/api/v1/equipos",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "No autenticado"


def test_change_password_invalidates_previous_access_token(unauthenticated_client):
    """Al cambiar contraseña, el JWT previo debe quedar inválido."""

    login_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200
    old_token = login_response.json()["access_token"]

    change_response = unauthenticated_client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "Admin123!", "new_password": "Admin123!Nueva"},
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert change_response.status_code == 200

    old_token_me_response = unauthenticated_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert old_token_me_response.status_code == 401

    login_with_new_password_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!Nueva"},
    )
    assert login_with_new_password_response.status_code == 200


def test_protected_endpoint_rejects_request_without_token(unauthenticated_client):
    """Valida rechazo de endpoints operativos sin autenticación."""

    response = unauthenticated_client.get("/api/v1/equipos")

    assert response.status_code == 401
    assert response.json()["detail"] in {"Not authenticated", "No autenticado"}


def test_jwt_contains_jti_for_revocation(unauthenticated_client):
    """Valida que el JWT incluya jti único para permitir revocación."""

    from app.config import get_settings

    login_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    settings = get_settings()
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    assert "jti" in payload, "JWT debe incluir jti para soportar revocación"
    assert isinstance(payload["jti"], str) and len(payload["jti"]) >= 16


def test_blacklisted_jwt_is_rejected_when_redis_reports_revocation(
    unauthenticated_client, monkeypatch
):
    """Valida que una entrada existente en Redis bloquee el JWT."""

    import redis

    from app import dependencies

    class FakeRedis:
        """Cliente mínimo para representar una blacklist activa."""

        def exists(self, key):
            assert key.startswith("blacklist:")
            return 1

    monkeypatch.setattr(dependencies.settings, "redis_url", "redis://redis:6379")
    monkeypatch.setattr(redis, "from_url", lambda *args, **kwargs: FakeRedis())

    login_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200

    response = unauthenticated_client.get(
        "/api/v1/equipos",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
    )

    assert response.status_code == 401


def test_revocation_redis_client_is_reused(monkeypatch):
    """La caché Redis de revocación debe reutilizar el pool entre requests."""

    import redis

    from app import dependencies

    fake_client = object()
    factory_calls = []

    monkeypatch.setattr(dependencies, "_revocation_redis_client", None)
    monkeypatch.setattr(dependencies, "_revocation_redis_config", None)
    monkeypatch.setattr(dependencies.settings, "redis_url", "redis://redis:6379")
    monkeypatch.setattr(
        redis,
        "from_url",
        lambda *args, **kwargs: factory_calls.append((args, kwargs)) or fake_client,
    )

    first_client = dependencies.get_revocation_redis_client()
    second_client = dependencies.get_revocation_redis_client()

    assert first_client is fake_client
    assert second_client is fake_client
    assert len(factory_calls) == 1


def test_logout_revokes_cookie_and_blocks_access(unauthenticated_client):
    """Valida flujo completo: login → usar token → logout → token cookie rechazado."""

    # 1. Login
    login_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    # 2. Usar token en endpoint protegido (header Authorization)
    equipos_response = unauthenticated_client.get(
        "/api/v1/equipos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert equipos_response.status_code == 200

    # 3. Logout con cookie
    logout_response = unauthenticated_client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 204

    # 4. Verificar que la cookie se borró
    set_cookie_header = logout_response.headers.get("set-cookie", "")
    assert "manttoai_token=" in set_cookie_header

    # 5. Sin cookie ni header → rechazado
    protected_response = unauthenticated_client.get("/api/v1/equipos")
    assert protected_response.status_code == 401

    # 6. Con el token viejo vía header debe seguir rechazado aunque no haya Redis.
    response = unauthenticated_client.get(
        "/api/v1/equipos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_logout_reports_persistence_failure_instead_of_claiming_success(
    unauthenticated_client, monkeypatch
):
    """No debe devolver 204 si la revocación persistente falló."""

    from app.routers import auth as auth_router
    from sqlalchemy.exc import SQLAlchemyError

    login_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200

    def fail_revoke(_db, _token):
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr(auth_router, "revoke_access_token", fail_revoke)

    logout_response = unauthenticated_client.post("/api/v1/auth/logout")

    assert logout_response.status_code == 503
    assert logout_response.json()["detail"] == "No se pudo revocar la sesión"


def test_logout_revokes_bearer_token_without_redis(unauthenticated_client, monkeypatch):
    """El logout debe revocar el JWT aunque Redis no esté configurado."""

    from app import dependencies
    from app.routers import auth as auth_router

    monkeypatch.setattr(dependencies.settings, "redis_url", "")
    monkeypatch.setattr(auth_router.settings, "redis_url", "")

    login_response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    logout_response = unauthenticated_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_response.status_code == 204

    session_local = unauthenticated_client.app.state.testing_session_local
    payload = jwt.decode(
        token,
        get_settings().secret_key,
        algorithms=["HS256"],
        options={"verify_exp": False},
    )
    with session_local() as db:
        assert (
            db.scalar(select(RevokedToken).where(RevokedToken.jti == payload["jti"]))
            is not None
        )

    replay_response = unauthenticated_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert replay_response.status_code == 401


def test_protected_endpoint_rejects_invalid_token(unauthenticated_client):
    """Valida rechazo de token inválido en endpoints protegidos."""

    response = unauthenticated_client.get(
        "/api/v1/equipos",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "No autenticado"


def test_update_profile_updates_only_allowed_fields(client):
    """Valida que perfil solo actualice nombre/avatar y preserve email."""

    response = client.put(
        "/api/v1/auth/profile",
        json={
            "nombre": "Admin Editado",
            "avatar": "avatar-03",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Admin Editado"
    assert data["avatar"] == "avatar-03"
    assert data["email"] == "admin@manttoai.local"


def test_update_profile_returns_500_when_commit_fails() -> None:
    """Valida manejo de error cuando falla commit durante update_profile."""

    class FakeDB:
        rollback_called = False

        def commit(self):
            raise RuntimeError("commit failed")

        def rollback(self):
            self.rollback_called = True

        def refresh(self, _usuario):
            return None

    fake_db = FakeDB()
    current_user = SimpleNamespace(
        id=1,
        nombre="Admin",
        email="admin@manttoai.local",
        rol="admin",
        avatar=None,
        telefono=None,
        created_at=None,
    )

    with pytest.raises(HTTPException) as exc_info:
        update_profile(
            payload=ProfileUpdate(nombre="Nombre que falla"),
            request=SimpleNamespace(),
            db=fake_db,
            current_user=current_user,
        )

    error = exc_info.value
    assert error.status_code == 500
    assert error.detail == "No se pudo actualizar el perfil"
    assert fake_db.rollback_called is True


def test_demo_user_cannot_change_shared_credentials_or_profile(client):
    """La cuenta demo compartida debe permanecer en modo lectura."""

    session_local = client.app.state.testing_session_local
    with session_local() as db:
        demo_user = Usuario(
            nombre="Demo ManttoAI",
            email="demo@manttoai.local",
            password_hash=hash_password("Demo1234!"),
            rol="visualizador",
            is_demo=True,
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        demo_token = create_access_token(str(demo_user.id))

    headers = {"Authorization": f"Bearer {demo_token}"}

    profile_response = client.put(
        "/api/v1/auth/profile",
        json={"nombre": "Visitante", "avatar": "avatar-03"},
        headers=headers,
    )
    password_response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "Demo1234!", "new_password": "Demo1234!Nueva"},
        headers=headers,
    )

    assert profile_response.status_code == 403
    assert profile_response.json()["detail"] == "La cuenta demo es de solo lectura"
    assert password_response.status_code == 403
    assert password_response.json()["detail"] == "La cuenta demo es de solo lectura"
