"""Servicio de negocio para gestión de Audit Logs."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
    usuario_id: int | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    """
    Crea un registro de auditoría manualmente.

    Args:
        db: Sesión de base de datos
        action: Acción realizada (create, update, delete, etc.)
        entity_type: Tipo de entidad (equipo, alerta, usuario, etc.)
        entity_id: ID de la entidad afectada
        old_values: Valores anteriores (para updates/deletes)
        new_values: Valores nuevos (para creates/updates)
        usuario_id: ID del usuario que realizó la acción
        ip_address: Dirección IP del request
        user_agent: User agent del request

    Returns:
        AuditLog: Objeto creado
    """

    audit_log = AuditLog(
        usuario_id=usuario_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.utcnow(),
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def get_audit_logs(
    db: Session,
    usuario_id: int | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    action: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[AuditLog], int]:
    """
    Retorna logs de auditoría con filtros opcionales.

    Returns:
        tuple: (lista de logs, total count)
    """

    from sqlalchemy import func

    query = select(AuditLog)

    if usuario_id:
        query = query.where(AuditLog.usuario_id == usuario_id)

    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)

    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)

    if action:
        query = query.where(AuditLog.action == action)

    # Contar total usando COUNT(*) - O(1) en la DB
    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0

    # Aplicar paginación
    query = query.order_by(AuditLog.created_at.desc())
    query = query.limit(limit).offset(offset)

    logs = list(db.scalars(query).all())

    return logs, total


def get_audit_log_by_id(db: Session, log_id: int) -> AuditLog | None:
    """Retorna un log de auditoría por ID."""

    return db.get(AuditLog, log_id)
