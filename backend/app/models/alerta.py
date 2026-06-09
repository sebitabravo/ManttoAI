"""Modelo de alerta."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Alerta(Base):
    """Representa una alerta generada por umbrales o predicción."""

    __tablename__ = "alertas"
    __table_args__ = (
        Index("ix_alertas_equipo_leida", "equipo_id", "leida"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    equipo_id: Mapped[int] = mapped_column(
        ForeignKey("equipos.id", ondelete="CASCADE"), index=True
    )
    organizacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizaciones.id"), nullable=True, index=True
    )
    tipo: Mapped[str] = mapped_column(String(50))
    mensaje: Mapped[str] = mapped_column(String(255))
    nivel: Mapped[str] = mapped_column(String(20), default="medio")
    email_enviado: Mapped[bool] = mapped_column(Boolean, default=False)
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
