"""Tests de equipos."""


def test_list_equipos_returns_demo_data(client):
    """Valida que el listado de equipos no venga vacío."""

    response = client.get("/equipos")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_create_equipo_returns_payload_with_id(client):
    """Valida la creación demo de equipos."""

    payload = {
        "nombre": "Ventilador",
        "ubicacion": "Planta piloto",
        "tipo": "Ventilador",
        "estado": "operativo",
    }
    response = client.post("/equipos", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] >= 1
