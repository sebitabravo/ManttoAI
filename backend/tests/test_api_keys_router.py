"""Tests de endpoints para gestión de API Keys."""


BASE_API_KEYS = "/api/v1/api-keys"


def test_create_get_list_and_revoke_api_key_flow(client):
    """Valida el flujo completo de creación, consulta, listado y revocación."""

    create_response = client.post(BASE_API_KEYS, json={"device_id": "esp32_linea_01"})
    assert create_response.status_code == 201

    created = create_response.json()
    assert created["device_id"] == "esp32_linea_01"
    assert created["is_active"] is True
    assert created["key"].startswith("mttk_")

    api_key_id = created["id"]

    get_response = client.get(f"{BASE_API_KEYS}/{api_key_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == api_key_id

    list_response = client.get(BASE_API_KEYS)
    assert list_response.status_code == 200
    ids = {item["id"] for item in list_response.json()}
    assert api_key_id in ids

    delete_response = client.delete(f"{BASE_API_KEYS}/{api_key_id}")
    assert delete_response.status_code == 204

    active_list_response = client.get(BASE_API_KEYS)
    assert active_list_response.status_code == 200
    active_ids = {item["id"] for item in active_list_response.json()}
    assert api_key_id not in active_ids

    inactive_list_response = client.get(
        BASE_API_KEYS,
        params={"include_inactive": True},
    )
    assert inactive_list_response.status_code == 200
    api_key_revocada = next(
        (item for item in inactive_list_response.json() if item["id"] == api_key_id),
        None,
    )
    assert api_key_revocada is not None
    assert api_key_revocada["is_active"] is False


def test_list_api_keys_filters_by_device_id(client):
    """Valida filtro por device_id en endpoint de listado."""

    first = client.post(BASE_API_KEYS, json={"device_id": "esp32_a"})
    second = client.post(BASE_API_KEYS, json={"device_id": "esp32_b"})
    assert first.status_code == 201
    assert second.status_code == 201

    filtered = client.get(BASE_API_KEYS, params={"device_id": "esp32_b"})
    assert filtered.status_code == 200
    payload = filtered.json()
    assert len(payload) == 1
    assert payload[0]["device_id"] == "esp32_b"


def test_create_api_key_rejects_duplicate_device_id(client):
    """Valida respuesta 400 cuando ya existe API Key activa para el dispositivo."""

    first = client.post(BASE_API_KEYS, json={"device_id": "esp32_dup"})
    assert first.status_code == 201

    duplicate = client.post(BASE_API_KEYS, json={"device_id": "esp32_dup"})
    assert duplicate.status_code == 400
    assert "Ya existe una API Key" in duplicate.json()["detail"]


def test_get_api_key_returns_404_when_not_found(client):
    """Valida not found cuando la API Key no existe."""

    response = client.get(f"{BASE_API_KEYS}/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "API Key no encontrada"


def test_delete_api_key_returns_404_when_not_found(client):
    """Valida not found al revocar una API Key inexistente."""

    response = client.delete(f"{BASE_API_KEYS}/99999")
    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"]
