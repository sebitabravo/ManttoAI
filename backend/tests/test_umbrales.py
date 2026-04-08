"""Tests de umbrales."""


def _build_equipo_payload(nombre: str) -> dict[str, str]:
    """Construye un payload válido para crear equipos."""

    return {
        "nombre": nombre,
        "ubicacion": "Planta piloto",
        "tipo": "Motor",
        "estado": "operativo",
    }


def _create_equipo(client, nombre: str = "Equipo Base") -> int:
    """Crea un equipo auxiliar y retorna su id."""

    response = client.post("/equipos", json=_build_equipo_payload(nombre))
    assert response.status_code == 201
    return response.json()["id"]


def _build_umbral_payload(
    equipo_id: int,
    variable: str = "temperatura",
    valor_min: float = 10.0,
    valor_max: float = 50.0,
) -> dict[str, int | float | str]:
    """Construye un payload válido para crear umbrales."""

    return {
        "equipo_id": equipo_id,
        "variable": variable,
        "valor_min": valor_min,
        "valor_max": valor_max,
    }


def test_list_umbrales_returns_persisted_records(client):
    """Valida que el listado lea umbrales reales desde la DB."""

    equipo_id = _create_equipo(client)
    client.post(
        "/umbrales",
        json=_build_umbral_payload(equipo_id=equipo_id, variable="temperatura"),
    )
    client.post(
        "/umbrales",
        json=_build_umbral_payload(equipo_id=equipo_id, variable="humedad"),
    )

    response = client.get("/umbrales")

    assert response.status_code == 200
    umbrales = response.json()
    assert len(umbrales) >= 2
    variables = {umbral["variable"] for umbral in umbrales}
    assert {"temperatura", "humedad"}.issubset(variables)


def test_get_umbrales_by_equipo_filter_and_route(client):
    """Valida listado de umbrales filtrado por equipo en query y ruta dedicada."""

    equipo_a = _create_equipo(client, "Equipo Umbral A")
    equipo_b = _create_equipo(client, "Equipo Umbral B")

    client.post(
        "/umbrales",
        json=_build_umbral_payload(equipo_id=equipo_a, variable="temperatura"),
    )
    client.post(
        "/umbrales",
        json=_build_umbral_payload(equipo_id=equipo_b, variable="vibracion"),
    )

    filtered_query = client.get("/umbrales", params={"equipo_id": equipo_a})
    filtered_route = client.get(f"/umbrales/equipo/{equipo_a}")

    assert filtered_query.status_code == 200
    assert filtered_route.status_code == 200
    assert all(item["equipo_id"] == equipo_a for item in filtered_query.json())
    assert all(item["equipo_id"] == equipo_a for item in filtered_route.json())


def test_create_umbral_rejects_unknown_equipo(client):
    """Valida que no se creen umbrales con equipo inexistente."""

    payload = _build_umbral_payload(equipo_id=99999)
    response = client.post("/umbrales", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Equipo no encontrado"


def test_create_umbral_rejects_invalid_range(client):
    """Valida que no se cree un umbral con límites invertidos."""

    equipo_id = _create_equipo(client)
    payload = _build_umbral_payload(equipo_id=equipo_id, valor_min=70.0, valor_max=20.0)

    response = client.post("/umbrales", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "valor_min no puede ser mayor que valor_max"


def test_create_umbral_persists_and_can_be_retrieved(client):
    """Valida que crear umbral lo persista y se pueda consultar."""

    equipo_id = _create_equipo(client)
    payload = _build_umbral_payload(equipo_id=equipo_id, variable="vibracion")

    create_response = client.post("/umbrales", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["equipo_id"] == equipo_id
    assert created["variable"] == "vibracion"

    get_response = client.get(f"/umbrales/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == created["id"]
    assert get_response.json()["variable"] == "vibracion"


def test_create_umbral_by_equipo_path_overrides_payload_equipo(client):
    """Valida POST /umbrales/equipo/{id} forzando consistencia de equipo."""

    equipo_a = _create_equipo(client, "Equipo Ruta A")
    equipo_b = _create_equipo(client, "Equipo Ruta B")

    response = client.post(
        f"/umbrales/equipo/{equipo_a}",
        json=_build_umbral_payload(equipo_id=equipo_b, variable="temperatura"),
    )

    assert response.status_code == 201
    assert response.json()["equipo_id"] == equipo_a


def test_update_umbral_persists_changes(client):
    """Valida que PUT actualice umbrales persistidos en DB."""

    equipo_id = _create_equipo(client)
    create_response = client.post(
        "/umbrales",
        json=_build_umbral_payload(equipo_id=equipo_id),
    )
    umbral_id = create_response.json()["id"]

    update_payload = {"valor_min": 12.5, "valor_max": 48.0}
    update_response = client.put(f"/umbrales/{umbral_id}", json=update_payload)

    assert update_response.status_code == 200
    assert update_response.json()["valor_min"] == 12.5
    assert update_response.json()["valor_max"] == 48.0

    get_response = client.get(f"/umbrales/{umbral_id}")

    assert get_response.status_code == 200
    assert get_response.json()["valor_min"] == 12.5
    assert get_response.json()["valor_max"] == 48.0


def test_update_umbral_rejects_invalid_range(client):
    """Valida que PUT rechace límites invertidos en umbral existente."""

    equipo_id = _create_equipo(client)
    create_response = client.post(
        "/umbrales",
        json=_build_umbral_payload(equipo_id=equipo_id, valor_min=10.0, valor_max=50.0),
    )
    umbral_id = create_response.json()["id"]

    update_response = client.put(
        f"/umbrales/{umbral_id}",
        json={"valor_min": 80.0, "valor_max": 10.0},
    )

    assert update_response.status_code == 422
    assert (
        update_response.json()["detail"] == "valor_min no puede ser mayor que valor_max"
    )

    get_response = client.get(f"/umbrales/{umbral_id}")
    assert get_response.status_code == 200
    assert get_response.json()["valor_min"] == 10.0
    assert get_response.json()["valor_max"] == 50.0


def test_put_umbral_not_found_returns_404(client):
    """Valida que PUT /umbrales/{id} responda 404 cuando no existe."""

    response = client.put("/umbrales/99999", json={"valor_min": 20.0})

    assert response.status_code == 404
    assert response.json()["detail"] == "Umbral no encontrado"


def test_delete_umbral_removes_record(client):
    """Valida que DELETE elimine un umbral existente."""

    equipo_id = _create_equipo(client)
    create_response = client.post(
        "/umbrales",
        json=_build_umbral_payload(equipo_id=equipo_id),
    )
    umbral_id = create_response.json()["id"]

    delete_response = client.delete(f"/umbrales/{umbral_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/umbrales/{umbral_id}")
    assert get_response.status_code == 404


def test_delete_umbral_not_found_returns_404(client):
    """Valida que DELETE /umbrales/{id} responda 404 cuando no existe."""

    response = client.delete("/umbrales/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Umbral no encontrado"
