"""Tests de autenticación."""


def test_login_endpoint_returns_token(client):
    """Valida que el login devuelva un token bearer."""

    response = client.post(
        "/auth/login", json={"email": "demo@example.com", "password": "123456"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_register_endpoint_returns_user(client):
    """Valida el endpoint de registro demo."""

    response = client.post(
        "/auth/register",
        json={
            "nombre": "Sebastián",
            "email": "sebastian@example.com",
            "password": "12345678",
            "rol": "admin",
        },
    )
    assert response.status_code == 200
    assert response.json()["email"] == "sebastian@example.com"
