"""Regresiones de aislamiento entre organizaciones."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.chat import MensajeChat
from app.models.equipo import Equipo
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario
from app.services.api_key_service import create_api_key
from app.services.audit_service import log_audit
from app.services.auth_service import create_access_token, hash_password

client = TestClient(app)


def _headers(user: Usuario) -> dict[str, str]:
    """Construye autenticación JWT para el usuario indicado."""

    return {"Authorization": f"Bearer {create_access_token(str(user.id))}"}


def _create_tenant_admins(db: Session) -> tuple[Usuario, Usuario]:
    """Crea dos administradores aislados para probar superficies agregadas."""

    org_a = Organizacion(nombre="Organización métricas A", rubro="industrial")
    org_b = Organizacion(nombre="Organización métricas B", rubro="comercial")
    db.add_all([org_a, org_b])
    db.flush()

    user_a = Usuario(
        nombre="Admin métricas A",
        email="admin-metrics-a@tenant.test",
        password_hash=hash_password("TenantMetricsA123!"),
        rol="admin",
        organizacion_id=org_a.id,
    )
    user_b = Usuario(
        nombre="Admin métricas B",
        email="admin-metrics-b@tenant.test",
        password_hash=hash_password("TenantMetricsB123!"),
        rol="admin",
        organizacion_id=org_b.id,
    )
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)
    return user_a, user_b


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


def test_admin_metrics_are_scoped_to_user_organization(db: Session):
    """Las métricas agregadas no deben revelar datos de otros tenants."""

    user_a, user_b = _create_tenant_admins(db)
    db.add_all(
        [
            Equipo(nombre="Equipo métricas A", organizacion_id=user_a.organizacion_id),
            Equipo(nombre="Equipo métricas B", organizacion_id=user_b.organizacion_id),
        ]
    )
    db.commit()

    response_a = client.get("/api/v1/metrics/summary", headers=_headers(user_a))
    response_b = client.get("/api/v1/metrics/summary", headers=_headers(user_b))

    assert response_a.status_code == 200
    assert response_b.status_code == 200
    assert response_a.json()["system"] == {
        "total_equipos": 1,
        "total_alertas_activas": 0,
        "total_lecturas_24h": 0,
        "total_usuarios": 1,
    }
    assert response_b.json()["system"] == response_a.json()["system"]


def test_admin_chat_history_and_export_are_scoped_to_user_organization(
    db: Session,
):
    """El historial y dataset exportado no deben cruzar organizaciones."""

    user_a, user_b = _create_tenant_admins(db)
    db.add_all(
        [
            MensajeChat(
                usuario_id=user_a.id,
                mensaje_usuario="mensaje privado tenant A",
                respuesta_ia="respuesta privada tenant A",
                fuente="reglas",
            ),
            MensajeChat(
                usuario_id=user_b.id,
                mensaje_usuario="mensaje privado tenant B",
                respuesta_ia="respuesta privada tenant B",
                fuente="reglas",
            ),
        ]
    )
    db.commit()

    history_response = client.get(
        "/api/v1/chat/historial", headers=_headers(user_b)
    )
    export_response = client.get(
        "/api/v1/chat/dataset-export", headers=_headers(user_b)
    )

    assert history_response.status_code == 200
    assert [row["mensaje_usuario"] for row in history_response.json()] == [
        "mensaje privado tenant B"
    ]
    assert export_response.status_code == 200
    assert "mensaje privado tenant B" in export_response.text
    assert "mensaje privado tenant A" not in export_response.text
