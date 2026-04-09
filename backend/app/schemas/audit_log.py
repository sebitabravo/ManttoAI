"""Schemas Pydantic para Audit Logs."""

from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Schema para respuesta de Audit Log."""

    id: int
    usuario_id: int | None
    action: str
    entity_type: str | None
    entity_id: int | None
    old_values: dict | None
    new_values: dict | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema para lista de Audit Logs."""

    logs: list[AuditLogResponse]
    total: int
    page: int
    per_page: int
