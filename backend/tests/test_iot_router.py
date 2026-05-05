"""Tests para router IoT autenticado con API Key."""

from types import SimpleNamespace

from starlette.requests import Request

from app.dependencies import get_api_key_user
from app.main import app
from app.routers.iot import _resolve_iot_rate_limit_key


def _build_lectura_payload(equipo_id: int) -> dict[str, float | int]:
    """Construye payload mínimo válido para endpoint IoT."""

    return {
        "equipo_id": equipo_id,
        "temperatura": 48.5,
        "humedad": 52.0,
        "vib_x": 0.2,
        "vib_y": 0.18,
        "vib_z": 9.7,
    }


def _create_equipo(client, nombre: str = "Equipo IoT") -> int:
    """Crea un equipo auxiliar para pruebas del endpoint IoT."""

    response = client.post(
        "/equipos",
        json={
            "nombre": nombre,
            "ubicacion": "Laboratorio",
            "tipo": "Motor",
            "estado": "operativo",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_rate_limit_key_uses_anonymous_when_header_is_missing() -> None:
    """Valida clave de rate limit anónima cuando no viene X-API-Key."""

    request = Request({"type": "http", "headers": []})
    assert _resolve_iot_rate_limit_key(request) == "anonymous"


def test_rate_limit_key_hashes_api_key_without_exposing_plain_value() -> None:
    """Valida hash de API key en clave de rate limit para evitar exposición."""

    request = Request(
        {
            "type": "http",
            "headers": [(b"x-api-key", b"mttk_demo_key_123")],
        }
    )
    value = _resolve_iot_rate_limit_key(request)
    assert value.startswith("api-key:")
    assert "mttk_demo_key_123" not in value


def test_post_lectura_iot_returns_401_when_api_key_is_missing(client):
    """Valida rechazo con 401 cuando no hay API key válida."""

    equipo_id = _create_equipo(client, "IoT sin API key")
    app.dependency_overrides[get_api_key_user] = lambda: None
    try:
        response = client.post(
            "/api/v1/iot/lecturas",
            json=_build_lectura_payload(equipo_id),
        )
    finally:
        app.dependency_overrides.pop(get_api_key_user, None)

    assert response.status_code == 401
    assert response.json()["detail"] == "API Key inválida o inactiva"


def test_post_lectura_iot_returns_403_when_api_key_device_does_not_match(client):
    """Valida rechazo con 403 cuando el device_id de API key no coincide."""

    equipo_id = _create_equipo(client, "IoT device mismatch")
    app.dependency_overrides[get_api_key_user] = lambda: SimpleNamespace(
        device_id="otro-equipo"
    )
    try:
        response = client.post(
            "/api/v1/iot/lecturas",
            json=_build_lectura_payload(equipo_id),
        )
    finally:
        app.dependency_overrides.pop(get_api_key_user, None)

    assert response.status_code == 403
    assert response.json()["detail"] == "API Key no autorizada para este equipo"


def test_post_lectura_iot_persists_reading_when_api_key_matches_device(client):
    """Valida creación exitosa de lectura cuando API key autoriza el equipo."""

    equipo_id = _create_equipo(client, "IoT OK")
    app.dependency_overrides[get_api_key_user] = lambda: SimpleNamespace(
        device_id=str(equipo_id)
    )
    try:
        response = client.post(
            "/api/v1/iot/lecturas",
            json=_build_lectura_payload(equipo_id),
        )
    finally:
        app.dependency_overrides.pop(get_api_key_user, None)

    assert response.status_code == 201
    data = response.json()
    assert data["equipo_id"] == equipo_id
    assert data["temperatura"] == 48.5
