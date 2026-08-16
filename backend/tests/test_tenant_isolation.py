"""Regresiones de aislamiento entre organizaciones."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario
from app.services.api_key_service import create_api_key
from app.services.audit_service import log_audit
from app.services.auth_service import create_access_token, hash_password

client = TestClient(app)


def _headers(user: Usuario) -> dict[str, str]:
    """Construye autenticación JWT para el usuario indicado."""

    return {"Authorization": f"Bearer {create_access_token(str(user.id))}"}


def test_authenticated_queries_are_scoped_to_user_organization(db: Session):
    """Un usuario no puede listar ni consultar equipos de otro tenant."""

    org_a = Organizacion(nombre="Organización A", rubro="industrial")
    org_b = Organizacion(nombre="Organización B", rubro="agricola")
    db.add_all([org_a, org_b])
    db.flush()

    user_a = Usuario(
        nombre="Admin A",
        email="admin-a@tenant.test",
        password_hash=hash_password("TenantA123!"),
        rol="admin",
        organizacion_id=org_a.id,
    )
    user_b = Usuario(
        nombre="Admin B",
        email="admin-b@tenant.test",
        password_hash=hash_password("TenantB123!"),
        rol="admin",
        organizacion_id=org_b.id,
    )
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)

    response_a = client.post(
        "/api/v1/equipos",
        json={"nombre": "Equipo privado A"},
        headers=_headers(user_a),
    )
    assert response_a.status_code == 201
    equipo_a_id = response_a.json()["id"]

    response_b_list = client.get("/api/v1/equipos", headers=_headers(user_b))
    assert response_b_list.status_code == 200
    assert response_b_list.json() == []

    response_b_get = client.get(
        f"/api/v1/equipos/{equipo_a_id}", headers=_headers(user_b)
    )
    assert response_b_get.status_code == 404

    response_b_reading = client.post(
        "/api/v1/lecturas",
        json={
            "equipo_id": equipo_a_id,
            "temperatura": 40,
            "humedad": 50,
            "vib_x": 0.1,
            "vib_y": 0.1,
            "vib_z": 9.8,
        },
        headers=_headers(user_b),
    )
    assert response_b_reading.status_code == 404


def test_admin_resources_are_scoped_to_user_organization(db: Session):
    """Usuarios, API keys y auditoría no deben cruzar tenants."""

    org_a = Organizacion(nombre="Organización A", rubro="industrial")
    org_b = Organizacion(nombre="Organización B", rubro="comercial")
    db.add_all([org_a, org_b])
    db.flush()

    user_a = Usuario(
        nombre="Admin A",
        email="admin-resources-a@tenant.test",
        password_hash=hash_password("TenantA123!"),
        rol="admin",
        organizacion_id=org_a.id,
    )
    user_b = Usuario(
        nombre="Admin B",
        email="admin-resources-b@tenant.test",
        password_hash=hash_password("TenantB123!"),
        rol="admin",
        organizacion_id=org_b.id,
    )
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)

    db.info["organizacion_id"] = org_a.id
    api_key, _ = create_api_key(
        db,
        device_id="tenant-a-device",
        created_by_id=user_a.id,
    )
    log_audit(
        db,
        action="create",
        entity_type="equipo",
        entity_id=1,
        usuario_id=user_a.id,
    )

    response_b_users = client.get("/api/v1/usuarios", headers=_headers(user_b))
    assert response_b_users.status_code == 200
    assert all(row["id"] != user_a.id for row in response_b_users.json()["usuarios"])

    response_b_key_list = client.get("/api/v1/api-keys", headers=_headers(user_b))
    assert response_b_key_list.status_code == 200
    assert response_b_key_list.json() == []

    response_b_key = client.get(
        f"/api/v1/api-keys/{api_key.id}", headers=_headers(user_b)
    )
    assert response_b_key.status_code == 404

    response_b_audit = client.get("/api/v1/audit-logs", headers=_headers(user_b))
    assert response_b_audit.status_code == 200
    assert all(
        row.get("usuario_id") != user_a.id for row in response_b_audit.json()["logs"]
    )
