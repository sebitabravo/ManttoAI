"""Tests de autenticación."""

from sqlalchemy import select

from app.models.usuario import Usuario
from app.services.auth_service import verify_password


def test_register_endpoint_persists_user_with_hashed_password(unauthenticated_client):
    """Valida que registro persista usuario real con contraseña hasheada."""

    payload = {
        "nombre": "Sebastián",
        "email": "sebastian@example.com",
        "password": "12345678",
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


def test_login_endpoint_rejects_invalid_credentials(unauthenticated_client):
    """Valida que login rechace credenciales inválidas."""

    response = unauthenticated_client.post(
        "/auth/login",
        json={"email": "admin@manttoai.local", "password": "incorrecta"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


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
