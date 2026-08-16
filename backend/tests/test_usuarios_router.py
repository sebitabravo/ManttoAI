"""Tests para el router de usuarios."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.models.api_key import APIKey
from app.models.audit_log import AuditLog
from app.models.usuario import Usuario

client = TestClient(app)


def test_list_usuarios_as_admin(db: Session, admin_user: Usuario, admin_token: str):
    """Test de listado de usuarios como admin."""

    response = client.get(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "usuarios" in data
    assert "total" in data
    assert len(data["usuarios"]) >= 1
    assert data["total"] >= 1


def test_list_usuarios_as_technico(
    db: Session, tecnico_user: Usuario, tecnico_token: str
):
    """Test que tecnico NO puede listar usuarios."""

    response = client.get(
        "/api/v1/usuarios",
        headers={"Authorization": f"Bearer {tecnico_token}"},
    )

    assert response.status_code == 403


def test_list_usuarios_as_unauthorized(db: Session):
    """Test que usuario no autenticado NO puede listar usuarios."""

    response = client.get("/api/v1/usuarios")

    assert response.status_code == 401


def test_create_usuario_as_admin(db: Session, admin_user: Usuario, admin_token: str):
    """Test de creación de usuario como admin."""

    payload = {
        "nombre": "Nuevo Usuario",
        "email": "nuevo@test.com",
        "password": "Test1234!",
        "rol": "tecnico",
    }

    response = client.post(
        "/api/v1/usuarios",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Nuevo Usuario"
    assert data["email"] == "nuevo@test.com"
    assert data["rol"] == "tecnico"
    assert "id" in data


def test_create_usuario_as_technico(
    db: Session, tecnico_user: Usuario, tecnico_token: str
):
    """Test que tecnico NO puede crear usuarios."""

    payload = {
        "nombre": "Nuevo Usuario",
        "email": "nuevo@test.com",
        "password": "Test1234!",
        "rol": "visualizador",
    }

    response = client.post(
        "/api/v1/usuarios",
        json=payload,
        headers={"Authorization": f"Bearer {tecnico_token}"},
    )

    assert response.status_code == 403


def test_create_usuario_duplicate_email(
    db: Session, admin_user: Usuario, admin_token: str
):
    """Test que no permite crear usuario con email duplicado."""

    payload = {
        "nombre": "Duplicado",
        "email": admin_user.email,  # Email duplicado
        "password": "Test1234!",
        "rol": "visualizador",
    }

    response = client.post(
        "/api/v1/usuarios",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 400


def test_get_usuario_by_id_as_admin(
    db: Session, admin_user: Usuario, tecnico_user: Usuario, admin_token: str
):
    """Test de obtención de usuario por ID como admin."""

    response = client.get(
        f"/api/v1/usuarios/{tecnico_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tecnico_user.id
    assert data["email"] == tecnico_user.email


def test_update_usuario_as_admin(db: Session, tecnico_user: Usuario, admin_token: str):
    """Test de actualización de usuario como admin."""

    payload = {"nombre": "Usuario Actualizado", "rol": "admin"}

    response = client.put(
        f"/api/v1/usuarios/{tecnico_user.id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Usuario Actualizado"
    assert data["rol"] == "admin"


def test_delete_usuario_as_admin(db: Session, tecnico_user: Usuario, admin_token: str):
    """Test de eliminación de usuario como admin."""

    response = client.delete(
        f"/api/v1/usuarios/{tecnico_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 204

    # Verificar que no existe
    response = client.get(
        f"/api/v1/usuarios/{tecnico_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


def test_delete_usuario_cleans_dependent_credentials_and_audit_logs(
    db: Session, tecnico_user: Usuario, admin_token: str
):
    """El borrado de usuario no debe fallar por referencias dependientes."""

    target_id = tecnico_user.id
    audit_log = AuditLog(
        usuario_id=target_id,
        action="login",
        entity_type="usuario",
        entity_id=target_id,
    )
    api_key = APIKey(
        key_hash="hash-de-prueba",
        key_prefix="mttk_test",
        device_id="device-delete-test",
        created_by_id=target_id,
    )
    db.add_all([audit_log, api_key])
    db.commit()

    response = client.delete(
        f"/api/v1/usuarios/{target_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 204
    db.expire_all()
    assert db.scalars(select(Usuario).where(Usuario.id == target_id)).first() is None
    assert (
        db.scalars(
            select(APIKey).where(APIKey.device_id == "device-delete-test")
        ).first()
        is None
    )
    assert db.get(AuditLog, audit_log.id).usuario_id is None


def test_delete_self_as_admin(db: Session, admin_user: Usuario, admin_token: str):
    """Test que admin NO puede eliminarse a sí mismo."""

    response = client.delete(
        f"/api/v1/usuarios/{admin_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 400


def test_list_usuarios_with_filters(
    db: Session, admin_user: Usuario, tecnico_user: Usuario, admin_token: str
):
    """Test de listado con filtros."""

    # Filtrar por rol
    response = client.get(
        "/api/v1/usuarios?rol=admin",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    for usuario in data["usuarios"]:
        assert usuario["rol"] == "admin"

    # Filtrar por paginación
    response = client.get(
        "/api/v1/usuarios?page=1&per_page=1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["usuarios"]) == 1
    assert data["total"] >= 2
