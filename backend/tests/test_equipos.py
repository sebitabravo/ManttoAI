"""Tests de equipos."""

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.routers import equipos as equipos_router


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


def _build_provision_token(purpose: str = "provision") -> str:
    """Construye un JWT válido para probar auto-registro/provisioning."""

    now = datetime.now(timezone.utc)
    payload = {
        "purpose": purpose,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    return jwt.encode(
        payload,
        equipos_router.settings.secret_key,
        algorithm=equipos_router.JWT_ALGORITHM,
    )


def test_get_provisioning_token_generates_valid_jwt(client):
    """Valida que el token de provisioning venga firmado y con propósito correcto."""

    response = client.get("/equipos/provisioning-token")

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "expires_at" in data

    claims = jwt.decode(
        data["token"],
        equipos_router.settings.secret_key,
        algorithms=[equipos_router.JWT_ALGORITHM],
    )
    assert claims["purpose"] == "provision"
    assert claims["exp"] > claims["iat"]


def test_full_setup_creates_equipo_and_umbrales_atomically(client):
    """Valida que full-setup cree equipo y ambos umbrales en una sola operación."""

    response = client.post(
        "/equipos/full-setup",
        json={
            "nombre": "Compresor Full Setup",
            "rubro": "industrial",
            "temperatura_max": 85.0,
            "vibracion_max": 0.7,
        },
    )

    assert response.status_code == 200
    data = response.json()
    equipo_id = data["equipo"]["id"]
    assert data["equipo"]["nombre"] == "Compresor Full Setup"
    assert isinstance(data["umbral_temperatura_id"], int)
    assert isinstance(data["umbral_vibracion_id"], int)

    umbrales_response = client.get(f"/umbrales/equipo/{equipo_id}")
    assert umbrales_response.status_code == 200
    variables = {umbral["variable"] for umbral in umbrales_response.json()}
    assert {"temperatura", "vibracion"} <= variables


def test_auto_register_creates_equipo_when_token_is_valid(unauthenticated_client):
    """Valida auto-registro de dispositivo con token de provisioning válido."""

    response = unauthenticated_client.post(
        "/equipos/auto-register",
        json={
            "token": _build_provision_token(),
            "mac_address": "AA:BB:CC:DD:EE:01",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["mac_address"] == "AA:BB:CC:DD:EE:01"
    assert data["nombre"].startswith("Equipo ")


def test_auto_register_rejects_invalid_token(unauthenticated_client):
    """Valida rechazo con 401 cuando el token JWT es inválido."""

    response = unauthenticated_client.post(
        "/equipos/auto-register",
        json={"token": "token-no-valido", "mac_address": "AA:BB:CC:DD:EE:02"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido"


def test_auto_register_rejects_wrong_token_purpose(unauthenticated_client):
    """Valida rechazo cuando el token no es para propósito de provisioning."""

    response = unauthenticated_client.post(
        "/equipos/auto-register",
        json={
            "token": _build_provision_token(purpose="auth"),
            "mac_address": "AA:BB:CC:DD:EE:03",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token no autorizado para provisioning"


def test_auto_register_requires_mac_address(unauthenticated_client):
    """Valida que mac_address es obligatoria para registrar el equipo."""

    response = unauthenticated_client.post(
        "/equipos/auto-register",
        json={
            "token": _build_provision_token(),
            "mac_address": None,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "mac_address es requerido"


def test_auto_register_returns_conflict_for_duplicate_mac(unauthenticated_client):
    """Valida conflicto al intentar registrar dos veces la misma MAC."""

    payload = {
        "token": _build_provision_token(),
        "mac_address": "AA:BB:CC:DD:EE:04",
    }
    first = unauthenticated_client.post("/equipos/auto-register", json=payload)
    assert first.status_code == 201

    second = unauthenticated_client.post("/equipos/auto-register", json=payload)
    assert second.status_code == 409
    assert second.json()["detail"] == "Equipo con esa MAC ya existe"


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
