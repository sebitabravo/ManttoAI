"""Tests de mantenciones."""


def _build_equipo_payload(nombre: str) -> dict[str, str]:
    """Construye un payload válido para crear equipos."""

    return {
        "nombre": nombre,
        "ubicacion": "Planta piloto",
        "tipo": "Motor",
        "estado": "operativo",
    }


def _create_equipo(client, nombre: str = "Equipo Mantención") -> int:
    """Crea un equipo auxiliar y retorna su id."""

    response = client.post("/equipos", json=_build_equipo_payload(nombre))
    assert response.status_code == 201
    return response.json()["id"]


def _build_mantencion_payload(
    equipo_id: int,
    tipo: str = "preventiva",
    descripcion: str = "Revisión mensual",
    estado: str = "programada",
) -> dict[str, int | str]:
    """Construye un payload válido para crear mantenciones."""

    return {
        "equipo_id": equipo_id,
        "tipo": tipo,
        "descripcion": descripcion,
        "estado": estado,
    }


def test_list_mantenciones_returns_persisted_records(client):
    """Valida que el listado lea mantenciones reales desde la DB."""

    equipo_id = _create_equipo(client)
    client.post(
        "/mantenciones",
        json=_build_mantencion_payload(
            equipo_id=equipo_id,
            tipo="preventiva",
            descripcion="Inspección mensual",
        ),
    )
    client.post(
        "/mantenciones",
        json=_build_mantencion_payload(
            equipo_id=equipo_id,
            tipo="correctiva",
            descripcion="Cambio de rodamiento",
        ),
    )

    response = client.get("/mantenciones")

    assert response.status_code == 200
    mantenciones = response.json()
    assert len(mantenciones) >= 2
    tipos = {mantencion["tipo"] for mantencion in mantenciones}
    assert {"preventiva", "correctiva"}.issubset(tipos)


def test_create_mantencion_rejects_unknown_equipo(client):
    """Valida que no se creen mantenciones con equipo inexistente."""

    payload = _build_mantencion_payload(equipo_id=99999)
    response = client.post("/mantenciones", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Equipo no encontrado"


def test_create_mantencion_persists_and_can_be_retrieved(client):
    """Valida que crear mantención la persista y se pueda consultar."""

    equipo_id = _create_equipo(client)
    payload = _build_mantencion_payload(
        equipo_id=equipo_id,
        tipo="predictiva",
        descripcion="Análisis de vibración",
    )

    create_response = client.post("/mantenciones", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["equipo_id"] == equipo_id
    assert created["tipo"] == "predictiva"

    get_response = client.get(f"/mantenciones/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == created["id"]
    assert get_response.json()["tipo"] == "predictiva"


def test_update_mantencion_persists_changes(client):
    """Valida que PUT actualice mantenciones persistidas en DB."""

    equipo_id = _create_equipo(client)
    create_response = client.post(
        "/mantenciones",
        json=_build_mantencion_payload(equipo_id=equipo_id),
    )
    mantencion_id = create_response.json()["id"]

    update_payload = {
        "descripcion": "Revisión trimestral completa",
        "estado": "ejecutada",
    }
    update_response = client.put(f"/mantenciones/{mantencion_id}", json=update_payload)

    assert update_response.status_code == 200
    assert update_response.json()["descripcion"] == "Revisión trimestral completa"
    assert update_response.json()["estado"] == "ejecutada"

    get_response = client.get(f"/mantenciones/{mantencion_id}")

    assert get_response.status_code == 200
    assert get_response.json()["descripcion"] == "Revisión trimestral completa"
    assert get_response.json()["estado"] == "ejecutada"


def test_put_mantencion_not_found_returns_404(client):
    """Valida que PUT /mantenciones/{id} responda 404 cuando no existe."""

    response = client.put("/mantenciones/99999", json={"estado": "ejecutada"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Mantención no encontrada"


def test_delete_mantencion_removes_record(client):
    """Valida que DELETE elimine una mantención existente."""

    equipo_id = _create_equipo(client)
    create_response = client.post(
        "/mantenciones",
        json=_build_mantencion_payload(equipo_id=equipo_id),
    )
    mantencion_id = create_response.json()["id"]

    delete_response = client.delete(f"/mantenciones/{mantencion_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/mantenciones/{mantencion_id}")
    assert get_response.status_code == 404


def test_delete_mantencion_not_found_returns_404(client):
    """Valida que DELETE /mantenciones/{id} responda 404 cuando no existe."""

    response = client.delete("/mantenciones/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Mantención no encontrada"
