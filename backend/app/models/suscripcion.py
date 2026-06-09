"""Modelos de planes y suscripciones para billing."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Plan(Base):
    """Plan de suscripcion disponible en el sistema."""

    __tablename__ = "planes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(50))
    slug: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    precio_mensual: Mapped[float] = mapped_column(Float)
    moneda: Mapped[str] = mapped_column(String(3), default="CLP")
    max_equipos: Mapped[int] = mapped_column(Integer)
    max_usuarios: Mapped[int] = mapped_column(Integer)
    sla_target: Mapped[float] = mapped_column(Float, default=99.5)
    features: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Suscripcion(Base):
    """Suscripcion activa de una organizacion a un plan."""

    __tablename__ = "suscripciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organizacion_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("organizaciones.id"), nullable=True, index=True, default=None
    )
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("planes.id"), index=True
    )
    estado: Mapped[str] = mapped_column(
        String(20), default="trial"
    )
    # IDs de suscripcion externa segun proveedor de pago
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    mercadopago_subscription_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
