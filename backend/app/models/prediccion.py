"""Modelo de predicción."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.organizacion import Organizacion


class Prediccion(Base):
    """Representa el resultado de una inferencia ML."""

    __tablename__ = "predicciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id", ondelete="CASCADE"), index=True)
    clasificacion: Mapped[str] = mapped_column(String(30), default="normal")
    probabilidad: Mapped[float] = mapped_column(Float, default=0.0)
    modelo_version: Mapped[str] = mapped_column(String(30), default="rf-mvp")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Multi-tenancy
    organizacion_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("organizaciones.id"), nullable=True, default=None
    )

    # Relación a organización (multi-tenancy)
    organizacion: Mapped["Organizacion | None"] = relationship("Organizacion")
