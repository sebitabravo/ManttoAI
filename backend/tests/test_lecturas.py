"""Tests de lecturas."""


def test_latest_lectura_returns_expected_shape(client):
    """Valida que exista una lectura demo por equipo."""

    response = client.get("/lecturas/latest/1")
    assert response.status_code == 200
    data = response.json()
    assert data["equipo_id"] == 1
    assert "temperatura" in data


def test_create_lectura_returns_created_record(client):
    """Valida la creación demo de una lectura."""

    payload = {
        "equipo_id": 1,
        "temperatura": 41.0,
        "humedad": 55.0,
        "vib_x": 0.3,
        "vib_y": 0.2,
        "vib_z": 9.8,
    }
    response = client.post("/lecturas", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == 99
