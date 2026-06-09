"""Schemas de SLA (Service Level Agreement) — uptime, downtime y reportes mensuales."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class SLAEventCreate(BaseModel):
    """Payload para registrar manualmente un evento de downtime."""

    event_type: Literal["outage", "degraded", "maintenance"]
    cause: str
    started_at: datetime | None = None
    equipo_id: int | None = None


class SLAEventResolve(BaseModel):
    """Payload para resolver un evento de downtime."""

    ended_at: datetime | None = None


class SLAEventResponse(BaseModel):
    """Representacion publica de un evento SLA."""

    id: int
    organizacion_id: int | None = None
    equipo_id: int | None = None
    event_type: str
    cause: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class SLAReportResponse(BaseModel):
    """Representacion publica de un reporte mensual SLA."""

    id: int
    organizacion_id: int | None = None
    month: str
    total_seconds: int
    downtime_seconds: int
    uptime_percentage: float
    sla_target: float
    met_sla: bool
    credits_amount: float
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
