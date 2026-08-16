"""Regresiones del contrato público versionado de la API."""


def test_operational_routes_use_api_v1_prefix(client):
    """Las rutas operativas no deben duplicarse en la raíz."""

    versioned_response = client.get("/api/v1/equipos")
    legacy_response = client.get("/equipos")

    assert versioned_response.status_code == 200
    assert legacy_response.status_code == 404


def test_auth_route_is_not_exposed_in_legacy_root(unauthenticated_client):
    """El login público debe usar únicamente el contrato /api/v1."""

    response = unauthenticated_client.post(
        "/auth/login",
        json={"email": "admin@manttoai.local", "password": "Admin123!"},
    )

    assert response.status_code == 404


def test_openapi_oauth_token_url_usa_ruta_versionada():
    """Swagger debe enviar credenciales al endpoint de login real."""

    from app.main import app

    schema = app.openapi()
    oauth_scheme = schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]

    assert oauth_scheme["flows"]["password"]["tokenUrl"] == "/api/v1/auth/login"
