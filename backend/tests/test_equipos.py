"""Tests de equipos."""

import secrets
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy import select

from app.models.equipo import Equipo
from app.models.provisioning_token import ProvisioningToken
from app.routers import equipos as equipos_router
from app.schemas.equipo import EquipoFullSetupRequest
from app.services import equipo_service


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

    client.post("/api/v1/equipos", json=_build_equipo_payload("Compresor A"))
    client.post("/api/v1/equipos", json=_build_equipo_payload("Compresor B"))

    response = client.get("/api/v1/equipos")
    assert response.status_code == 200

    equipos = response.json()
    assert len(equipos) >= 2
    nombres = {equipo["nombre"] for equipo in equipos}
    assert {"Compresor A", "Compresor B"}.issubset(nombres)


def test_get_equipo_not_found_returns_404(client):
    """Valida que GET /equipos/{id} responda 404 cuando no existe."""

    response = client.get("/api/v1/equipos/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Equipo no encontrado"


def _build_provision_token(
    expected_mac: str = "AA:BB:CC:DD:EE:01",
    purpose: str = "provision",
    jti: str | None = None,
) -> str:
    """Construye un JWT válido para probar auto-registro/provisioning."""

    now = datetime.now(timezone.utc)
    payload = {
        "purpose": purpose,
        "expected_mac": expected_mac,
        "jti": jti or secrets.token_urlsafe(16),
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

    response = client.get(
        "/api/v1/equipos/provisioning-token",
        params={"mac_address": "AA:BB:CC:DD:EE:10"},
    )

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
    assert claims["expected_mac"] == "AA:BB:CC:DD:EE:10"
    assert claims["jti"]
    assert claims["exp"] > claims["iat"]

    session_local = client.app.state.testing_session_local
    with session_local() as db:
        record = db.scalars(
            select(ProvisioningToken).where(ProvisioningToken.jti == claims["jti"])
        ).first()
        assert record is not None
        assert record.expected_mac == "AA:BB:CC:DD:EE:10"


def test_full_setup_creates_equipo_and_umbrales_atomically(client):
    """Valida que full-setup cree equipo y ambos umbrales en una sola operación."""

    response = client.post(
        "/api/v1/equipos/full-setup",
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

    umbrales_response = client.get(f"/api/v1/umbrales/equipo/{equipo_id}")
    assert umbrales_response.status_code == 200
    variables = {umbral["variable"] for umbral in umbrales_response.json()}
    assert {"temperatura", "vibracion"} <= variables


def test_full_setup_service_owns_transaction_and_persists_mac(db):
    """El servicio encapsula la transacción y conserva la MAC del payload."""

    payload = EquipoFullSetupRequest(
        nombre="Compresor Servicio",
        mac_address="AA:BB:CC:DD:EE:11",
        temperatura_max=82.0,
        vibracion_max=0.8,
    )

    equipo, umbral_temp, umbral_vib = equipo_service.create_equipo_with_umbrales(
        db, payload
    )

    assert equipo.id is not None
    assert equipo.mac_address == payload.mac_address
    assert umbral_temp.id is not None
    assert umbral_vib.id is not None


def _persist_provision_token(client, token: str) -> None:
    """Persiste en la fixture el registro que respalda un JWT de test."""

    claims = jwt.decode(
        token,
        equipos_router.settings.secret_key,
        algorithms=[equipos_router.JWT_ALGORITHM],
    )
    now = datetime.now(timezone.utc)
    session_local = client.app.state.testing_session_local
    with session_local() as db:
        db.add(
            ProvisioningToken(
                jti=claims["jti"],
                expected_mac=claims["expected_mac"],
                organizacion_id=claims.get("organizacion_id"),
                expires_at=datetime.fromtimestamp(claims["exp"], tz=timezone.utc),
                created_at=now,
            )
        )
        db.commit()


def test_auto_register_creates_equipo_when_token_is_valid(unauthenticated_client):
    """Valida auto-registro de dispositivo con token de provisioning válido."""

    token = _build_provision_token("AA:BB:CC:DD:EE:01")
    _persist_provision_token(unauthenticated_client, token)
    response = unauthenticated_client.post(
        "/api/v1/equipos/auto-register",
        json={
            "token": token,
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
        "/api/v1/equipos/auto-register",
        json={"token": "token-no-valido", "mac_address": "AA:BB:CC:DD:EE:02"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido"


def test_auto_register_rejects_wrong_token_purpose(unauthenticated_client):
    """Valida rechazo cuando el token no es para propósito de provisioning."""

    response = unauthenticated_client.post(
        "/api/v1/equipos/auto-register",
        json={
            "token": _build_provision_token("AA:BB:CC:DD:EE:03", purpose="auth"),
            "mac_address": "AA:BB:CC:DD:EE:03",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token no autorizado para provisioning"


def test_auto_register_requires_mac_address(unauthenticated_client):
    """Valida que mac_address es obligatoria para registrar el equipo."""

    response = unauthenticated_client.post(
        "/api/v1/equipos/auto-register",
        json={
            "token": _build_provision_token("AA:BB:CC:DD:EE:04"),
            "mac_address": None,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "mac_address es requerido"


def test_auto_register_consumes_token_after_success(unauthenticated_client):
    """Un provisioning JWT usado no puede registrarse otra vez aunque se borre el equipo."""

    token = _build_provision_token("AA:BB:CC:DD:EE:04")
    _persist_provision_token(unauthenticated_client, token)
    payload = {
        "token": token,
        "mac_address": "AA:BB:CC:DD:EE:04",
    }
    first = unauthenticated_client.post("/api/v1/equipos/auto-register", json=payload)
    assert first.status_code == 201

    session_local = unauthenticated_client.app.state.testing_session_local
    with session_local() as db:
        equipo = db.scalars(
            select(Equipo).where(Equipo.mac_address == "AA:BB:CC:DD:EE:04")
        ).first()
        assert equipo is not None
        db.delete(equipo)
        token_record = db.scalars(
            select(ProvisioningToken).where(
                ProvisioningToken.jti
                == jwt.decode(
                    token,
                    equipos_router.settings.secret_key,
                    algorithms=[equipos_router.JWT_ALGORITHM],
                )["jti"]
            )
        ).first()
        assert token_record is not None
        assert token_record.used_at is not None
        db.commit()

    second = unauthenticated_client.post("/api/v1/equipos/auto-register", json=payload)
    assert second.status_code == 409
    assert second.json()["detail"] == "Token de provisioning ya utilizado"


def test_auto_register_rejects_mac_different_from_token(unauthenticated_client):
    """Un token de provisioning queda ligado a la MAC solicitada."""

    response = unauthenticated_client.post(
        "/api/v1/equipos/auto-register",
        json={
            "token": _build_provision_token("AA:BB:CC:DD:EE:05"),
            "mac_address": "AA:BB:CC:DD:EE:06",
        },
    )

    assert response.status_code == 403


def test_create_equipo_persists_and_can_be_retrieved(client):
    """Valida que crear equipo lo persista y pueda consultarse."""

    payload = _build_equipo_payload("Ventilador")
    create_response = client.post("/api/v1/equipos", json=payload)

    assert create_response.status_code == 201

    created = create_response.json()
    assert "Location" in create_response.headers
    assert create_response.headers["Location"].endswith(
        f"/api/v1/equipos/{created['id']}"
    )

    get_response = client.get(f"/api/v1/equipos/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["nombre"] == "Ventilador"


def test_update_equipo_persists_changes(client):
    """Valida que PUT actualice datos reales en la DB."""

    create_response = client.post(
        "/api/v1/equipos", json=_build_equipo_payload("Motor X")
    )
    equipo_id = create_response.json()["id"]

    update_payload = {"estado": "monitoreo", "ubicacion": "Sala de bombas"}
    update_response = client.put(f"/api/v1/equipos/{equipo_id}", json=update_payload)

    assert update_response.status_code == 200
    assert update_response.json()["estado"] == "monitoreo"
    assert update_response.json()["ubicacion"] == "Sala de bombas"

    get_response = client.get(f"/api/v1/equipos/{equipo_id}")
    assert get_response.status_code == 200
    assert get_response.json()["estado"] == "monitoreo"


def test_put_equipo_not_found_returns_404(client):
    """Valida que PUT /equipos/{id} responda 404 cuando no existe."""

    response = client.put("/api/v1/equipos/99999", json={"estado": "monitoreo"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Equipo no encontrado"


def test_delete_equipo_removes_record(client):
    """Valida que DELETE elimine el equipo y luego responda 404."""

    create_response = client.post(
        "/api/v1/equipos", json=_build_equipo_payload("Bomba Norte")
    )
    equipo_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/equipos/{equipo_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/equipos/{equipo_id}")
    assert get_response.status_code == 404


def test_delete_equipo_not_found_returns_404(client):
    """Valida que DELETE /equipos/{id} responda 404 cuando no existe."""

    response = client.delete("/api/v1/equipos/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Equipo no encontrado"
