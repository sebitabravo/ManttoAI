"""Tests para el router de usuarios."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
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
        "password": "password123",
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
        "password": "password123",
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
        "password": "password123",
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
