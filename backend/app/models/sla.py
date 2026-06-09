"""Modelos para SLA monitoring (downtime y cumplimiento mensual)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SLAEvent(Base):
    """Registra un evento de downtime, degradacion o mantenimiento programado."""

    __tablename__ = "sla_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organizacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizaciones.id"), nullable=True, index=True
    )
    equipo_id: Mapped[int | None] = mapped_column(
        ForeignKey("equipos.id"), nullable=True, index=True
    )
    # "outage", "degraded", "maintenance"
    event_type: Mapped[str] = mapped_column(String(30))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cause: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SLAReport(Base):
    """Reporte mensual de cumplimiento SLA para una organizacion."""

    __tablename__ = "sla_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organizacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizaciones.id"), nullable=True, index=True
    )
    # formato "2026-06"
    month: Mapped[str] = mapped_column(String(7), index=True)
    total_seconds: Mapped[int] = mapped_column(Integer)
    downtime_seconds: Mapped[int] = mapped_column(Integer, default=0)
    uptime_percentage: Mapped[float] = mapped_column(Float)
    sla_target: Mapped[float] = mapped_column(Float)
    met_sla: Mapped[bool] = mapped_column(Boolean)
    credits_amount: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
