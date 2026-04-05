"""Tests de equipos."""


def _build_equipo_payload(nombre: str) -> dict[str, str]:
    """Construye un payload válido para crear equipos."""

    return {
        "nombre": nombre,
        "ubicacion": "Planta piloto",
        "tipo": "Motor",
        "estado": "operativo",
    }


def test_list_equipos_returns_persisted_records(client):
    """Valida que el listado lea equipos persistidos en la DB."""

    client.post("/equipos", json=_build_equipo_payload("Compresor A"))
    client.post("/equipos", json=_build_equipo_payload("Compresor B"))

    response = client.get("/equipos")
    assert response.status_code == 200

    equipos = response.json()
    assert len(equipos) >= 2
    nombres = {equipo["nombre"] for equipo in equipos}
    assert {"Compresor A", "Compresor B"}.issubset(nombres)


def test_get_equipo_not_found_returns_404(client):
    """Valida que GET /equipos/{id} responda 404 cuando no existe."""

    response = client.get("/equipos/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Equipo no encontrado"


def test_create_equipo_persists_and_can_be_retrieved(client):
    """Valida que crear equipo lo persista y pueda consultarse."""

    payload = _build_equipo_payload("Ventilador")
    create_response = client.post("/equipos", json=payload)

    assert create_response.status_code == 201

    created = create_response.json()
    assert "Location" in create_response.headers
    assert create_response.headers["Location"].endswith(f"/equipos/{created['id']}")

    get_response = client.get(f"/equipos/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["nombre"] == "Ventilador"


def test_update_equipo_persists_changes(client):
    """Valida que PUT actualice datos reales en la DB."""

    create_response = client.post("/equipos", json=_build_equipo_payload("Motor X"))
    equipo_id = create_response.json()["id"]

    update_payload = {"estado": "monitoreo", "ubicacion": "Sala de bombas"}
    update_response = client.put(f"/equipos/{equipo_id}", json=update_payload)

    assert update_response.status_code == 200
    assert update_response.json()["estado"] == "monitoreo"
    assert update_response.json()["ubicacion"] == "Sala de bombas"

    get_response = client.get(f"/equipos/{equipo_id}")
    assert get_response.status_code == 200
    assert get_response.json()["estado"] == "monitoreo"


def test_put_equipo_not_found_returns_404(client):
    """Valida que PUT /equipos/{id} responda 404 cuando no existe."""

    response = client.put("/equipos/99999", json={"estado": "monitoreo"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Equipo no encontrado"


def test_delete_equipo_removes_record(client):
    """Valida que DELETE elimine el equipo y luego responda 404."""

    create_response = client.post("/equipos", json=_build_equipo_payload("Bomba Norte"))
    equipo_id = create_response.json()["id"]

    delete_response = client.delete(f"/equipos/{equipo_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/equipos/{equipo_id}")
    assert get_response.status_code == 404


def test_delete_equipo_not_found_returns_404(client):
    """Valida que DELETE /equipos/{id} responda 404 cuando no existe."""

    response = client.delete("/equipos/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Equipo no encontrado"
