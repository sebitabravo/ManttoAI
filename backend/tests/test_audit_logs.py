"""Tests para el servicio de Audit Logs."""

import pytest
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.usuario import Usuario
from app.services.audit_service import (
    get_audit_log_by_id,
    get_audit_logs,
    log_audit,
)


def test_log_audit(db: Session, admin_user: Usuario):
    """Test de creación de log de auditoría."""

    audit_log = log_audit(
        db=db,
        action="create",
        entity_type="equipo",
        entity_id=1,
        old_values=None,
        new_values={"nombre": "Equipo Test", "ubicacion": "Test"},
        usuario_id=admin_user.id,
        ip_address="127.0.0.1",
        user_agent="test-agent",
    )

    assert audit_log.id is not None
    assert audit_log.action == "create"
    assert audit_log.entity_type == "equipo"
    assert audit_log.entity_id == 1
    assert audit_log.usuario_id == admin_user.id
    assert audit_log.ip_address == "127.0.0.1"
    assert audit_log.user_agent == "test-agent"
    assert audit_log.new_values == {"nombre": "Equipo Test", "ubicacion": "Test"}


def test_log_audit_without_user(db: Session):
    """Test de log de auditoría sin usuario (acciones de sistema)."""

    audit_log = log_audit(
        db=db,
        action="system",
        entity_type="system",
        old_values=None,
        new_values={"message": "System startup"},
        usuario_id=None,
        ip_address=None,
        user_agent=None,
    )

    assert audit_log.usuario_id is None
    assert audit_log.ip_address is None
    assert audit_log.user_agent is None


def test_get_audit_logs(db: Session, admin_user: Usuario, tecnico_user: Usuario):
    """Test de listado de logs con filtros."""

    # Crear varios logs
    log_audit(
        db,
        action="create",
        entity_type="equipo",
        entity_id=1,
        usuario_id=admin_user.id,
    )
    log_audit(
        db,
        action="delete",
        entity_type="alerta",
        entity_id=1,
        usuario_id=admin_user.id,
    )
    log_audit(
        db,
        action="update",
        entity_type="equipo",
        entity_id=2,
        usuario_id=tecnico_user.id,
    )

    # Listar todos
    logs, total = get_audit_logs(db)
    assert len(logs) >= 3
    assert total >= 3

    # Filtrar por usuario
    admin_logs, admin_total = get_audit_logs(db, usuario_id=admin_user.id)
    assert len(admin_logs) == 2
    assert admin_total == 2

    # Filtrar por acción
    create_logs, create_total = get_audit_logs(db, action="create")
    assert len(create_logs) >= 1

    # Filtrar por entidad
    equipo_logs, equipo_total = get_audit_logs(db, entity_type="equipo")
    assert len(equipo_logs) >= 2


def test_get_audit_logs_pagination(db: Session, admin_user: Usuario):
    """Test de paginación de logs."""

    # Crear 15 logs
    for i in range(15):
        log_audit(
            db,
            action="create",
            entity_type="test",
            entity_id=i,
            usuario_id=admin_user.id,
        )

    # Primera página (10 resultados)
    page1, total1 = get_audit_logs(db, limit=10, offset=0)
    assert len(page1) == 10
    assert total1 == 15

    # Segunda página (5 resultados)
    page2, total2 = get_audit_logs(db, limit=10, offset=10)
    assert len(page2) == 5
    assert total2 == 15


def test_get_audit_log_by_id(db: Session, admin_user: Usuario):
    """Test de obtención de log por ID."""

    created_log = log_audit(
        db,
        action="create",
        entity_type="equipo",
        entity_id=1,
        usuario_id=admin_user.id,
    )

    retrieved_log = get_audit_log_by_id(db, created_log.id)

    assert retrieved_log is not None
    assert retrieved_log.id == created_log.id
    assert retrieved_log.action == "create"


def test_get_audit_log_by_id_not_found(db: Session):
    """Test de log no encontrado."""

    log = get_audit_log_by_id(db, 99999)
    assert log is None


def test_audit_middleware_registra_lectura_admin(client):
    """Debe registrar lectura de endpoint sensible en contexto admin."""

    # GET sensible (usuarios) debe crear audit log de tipo read.
    response = client.get("/api/v1/usuarios")
    assert response.status_code == 200

    logs_response = client.get("/api/v1/audit-logs?page=1&per_page=10")
    assert logs_response.status_code == 200

    payload = logs_response.json()
    assert payload["total"] >= 1

    latest = payload["logs"][0]
    assert latest["action"] == "read"
    assert latest["entity_type"] == "usuario"
