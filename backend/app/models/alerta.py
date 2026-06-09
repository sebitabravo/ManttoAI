"""Modelo de alerta."""

from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.organizacion import Organizacion


class Alerta(Base):
    """Representa una alerta generada por umbrales o predicción."""

    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id", ondelete="CASCADE"), index=True)
    tipo: Mapped[str] = mapped_column(String(50))
    mensaje: Mapped[str] = mapped_column(String(255))
    nivel: Mapped[str] = mapped_column(String(20), default="medio")
    email_enviado: Mapped[bool] = mapped_column(Boolean, default=False)
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Multi-tenancy
    organizacion_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("organizaciones.id"), nullable=True, default=None
    )

    # Relación a organización (multi-tenancy)
    organizacion: Mapped["Organizacion | None"] = relationship("Organizacion")
