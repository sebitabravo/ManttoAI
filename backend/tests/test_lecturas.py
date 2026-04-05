"""Tests de lecturas."""


def _build_equipo_payload(nombre: str) -> dict[str, str]:
    """Construye un payload válido para crear equipos."""

    return {
        "nombre": nombre,
        "ubicacion": "Planta piloto",
        "tipo": "Motor",
        "estado": "operativo",
    }


def _create_equipo(client, nombre: str = "Equipo Lecturas") -> int:
    """Crea un equipo auxiliar y retorna su id."""

    response = client.post("/equipos", json=_build_equipo_payload(nombre))
    assert response.status_code == 201
    return response.json()["id"]


def _build_lectura_payload(
    equipo_id: int,
    temperatura: float = 41.0,
    humedad: float = 55.0,
    vib_x: float = 0.3,
    vib_y: float = 0.2,
    vib_z: float = 9.8,
) -> dict[str, int | float]:
    """Construye un payload válido para crear lecturas."""

    return {
        "equipo_id": equipo_id,
        "temperatura": temperatura,
        "humedad": humedad,
        "vib_x": vib_x,
        "vib_y": vib_y,
        "vib_z": vib_z,
    }


def test_create_lectura_persists_and_list_endpoint_reads_db(client):
    """Valida que POST persista y GET /lecturas lea desde DB real."""

    equipo_id = _create_equipo(client)
    payload = _build_lectura_payload(equipo_id=equipo_id, temperatura=43.2)

    create_response = client.post("/lecturas", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["equipo_id"] == equipo_id
    assert created["temperatura"] == 43.2

    list_response = client.get("/lecturas", params={"equipo_id": equipo_id})

    assert list_response.status_code == 200
    lecturas = list_response.json()
    assert len(lecturas) == 1
    assert lecturas[0]["id"] == created["id"]


def test_latest_lectura_returns_last_persisted_record(client):
    """Valida que GET /lecturas/latest/{equipo_id} lea última lectura real."""

    equipo_id = _create_equipo(client)
    client.post(
        "/lecturas", json=_build_lectura_payload(equipo_id=equipo_id, temperatura=38.5)
    )
    client.post(
        "/lecturas", json=_build_lectura_payload(equipo_id=equipo_id, temperatura=47.1)
    )

    response = client.get(f"/lecturas/latest/{equipo_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["equipo_id"] == equipo_id
    assert data["temperatura"] == 47.1


def test_create_lectura_rejects_unknown_equipo(client):
    """Valida que no se creen lecturas para equipos inexistentes."""

    payload = _build_lectura_payload(equipo_id=99999)
    response = client.post("/lecturas", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Equipo no encontrado"


def test_latest_lectura_not_found_returns_404(client):
    """Valida que latest responda 404 si el equipo no tiene lecturas."""

    equipo_id = _create_equipo(client)
    response = client.get(f"/lecturas/latest/{equipo_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Lectura no encontrada para el equipo"
