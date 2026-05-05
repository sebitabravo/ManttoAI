"""Tests de autenticación."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.models.usuario import Usuario
from app.routers.auth import update_profile
from app.schemas.usuario import ProfileUpdate
from app.services.auth_service import create_access_token, verify_password


def test_register_endpoint_persists_user_with_hashed_password(unauthenticated_client):
    """Valida que registro persista usuario real con contraseña hasheada."""

    payload = {
        "nombre": "Sebastián",
        "email": "sebastian@example.com",
        "password": "Test1234",
        "rol": "admin",
    }

    response = unauthenticated_client.post("/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]

    session_local = unauthenticated_client.app.state.testing_session_local
    with session_local() as db:
        usuario = db.scalars(
            select(Usuario).where(Usuario.email == payload["email"])
        ).first()

    assert usuario is not None
    assert usuario.password_hash != payload["password"]
    assert verify_password(payload["password"], usuario.password_hash)


def test_login_endpoint_returns_token_for_valid_credentials(unauthenticated_client):
    """Valida que login retorne token cuando credenciales son correctas."""

    response = unauthenticated_client.post(
        "/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_endpoint_v1_route_returns_token_for_valid_credentials(
    unauthenticated_client,
):
    """Valida que login funcione también bajo prefijo /api/v1."""

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
        "/auth/login",
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
        "/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200

    response = unauthenticated_client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "admin@manttoai.local"


def test_protected_endpoint_accepts_http_only_cookie_authentication(
    unauthenticated_client,
):
    """Valida acceso autenticado aun sin header Authorization explícito."""

    login_response = unauthenticated_client.post(
        "/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200

    response = unauthenticated_client.get("/equipos")

    assert response.status_code == 200


def test_cookie_auth_requires_csrf_header_for_mutations(unauthenticated_client):
    """Valida protección CSRF cuando la sesión web usa cookie HttpOnly."""

    login_response = unauthenticated_client.post(
        "/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200

    payload = {
        "nombre": "Equipo demo",
        "ubicacion": "Laboratorio",
        "tipo": "Motor",
        "estado": "operativo",
    }

    blocked_response = unauthenticated_client.post("/equipos", json=payload)
    assert blocked_response.status_code == 403

    csrf_token = unauthenticated_client.cookies.get("manttoai_csrf")
    allowed_response = unauthenticated_client.post(
        "/equipos",
        json=payload,
        headers={"X-CSRF-Token": csrf_token},
    )
    assert allowed_response.status_code == 201


def test_logout_endpoint_clears_auth_cookie(unauthenticated_client):
    """Valida cierre de sesión borrando cookie y bloqueando acceso posterior."""

    login_response = unauthenticated_client.post(
        "/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200

    logout_response = unauthenticated_client.post("/auth/logout")

    assert logout_response.status_code == 204
    assert "manttoai_token=" in logout_response.headers.get("set-cookie", "")

    protected_response = unauthenticated_client.get("/equipos")
    assert protected_response.status_code == 401


def test_login_endpoint_rejects_invalid_credentials(unauthenticated_client):
    """Valida que login rechace credenciales inválidas."""

    response = unauthenticated_client.post(
        "/auth/login",
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
        "/auth/login",
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

    token = create_access_token("admin@manttoai.local")
    response = unauthenticated_client.get(
        "/equipos",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "No autenticado"


def test_change_password_invalidates_previous_access_token(unauthenticated_client):
    """Al cambiar contraseña, el JWT previo debe quedar inválido."""

    login_response = unauthenticated_client.post(
        "/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )
    assert login_response.status_code == 200
    old_token = login_response.json()["access_token"]

    change_response = unauthenticated_client.post(
        "/auth/change-password",
        json={"current_password": "Admin123!", "new_password": "Admin123!Nueva"},
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert change_response.status_code == 200

    old_token_me_response = unauthenticated_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert old_token_me_response.status_code == 401

    login_with_new_password_response = unauthenticated_client.post(
        "/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!Nueva"},
    )
    assert login_with_new_password_response.status_code == 200


def test_protected_endpoint_rejects_request_without_token(unauthenticated_client):
    """Valida rechazo de endpoints operativos sin autenticación."""

    response = unauthenticated_client.get("/equipos")

    assert response.status_code == 401
    assert response.json()["detail"] in {"Not authenticated", "No autenticado"}


def test_protected_endpoint_rejects_invalid_token(unauthenticated_client):
    """Valida rechazo de token inválido en endpoints protegidos."""

    response = unauthenticated_client.get(
        "/equipos",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "No autenticado"


def test_update_profile_updates_only_allowed_fields(client):
    """Valida que perfil solo actualice nombre/avatar y preserve email."""

    response = client.put(
        "/auth/profile",
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
