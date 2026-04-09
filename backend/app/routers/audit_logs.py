"""Endpoints de consulta de Audit Logs."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_role
from app.middleware.rate_limit import limiter
from app.models.audit_log import AuditLog
from app.models.usuario import Usuario
from app.schemas.audit_log import AuditLogListResponse, AuditLogResponse
from app.services.audit_service import get_audit_log_by_id, get_audit_logs

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=AuditLogListResponse)
@limiter.limit("100/hour")  # Audit logs pueden ser muchos, limitar
def list_audit_logs(
    request: Request,
    usuario_id: int | None = Query(None, description="Filtrar por ID de usuario"),
    entity_type: str | None = Query(None, description="Filtrar por tipo de entidad"),
    entity_id: int | None = Query(None, description="Filtrar por ID de entidad"),
    action: str | None = Query(None, description="Filtrar por acción"),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(50, ge=1, le=100, description="Resultados por página"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> AuditLogListResponse:
    """Lista logs de auditoría con filtros (solo admin)."""

    offset = (page - 1) * per_page
    logs, total = get_audit_logs(
        db,
        usuario_id=usuario_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        limit=per_page,
        offset=offset,
    )

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{log_id}", response_model=AuditLogResponse)
@limiter.limit("200/hour")
def get_audit_log(
    log_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> AuditLogResponse:
    """Retorna un log de auditoría por ID (solo admin)."""

    log = get_audit_log_by_id(db, log_id)
    if not log:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Audit Log no encontrado"
        )

    return AuditLogResponse.model_validate(log)
