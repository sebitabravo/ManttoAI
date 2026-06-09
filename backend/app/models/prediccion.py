"""Modelo de predicción."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Prediccion(Base):
    """Representa el resultado de una inferencia ML."""

    __tablename__ = "predicciones"
    __table_args__ = (
        Index("ix_predicciones_equipo_created_at", "equipo_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    equipo_id: Mapped[int] = mapped_column(
        ForeignKey("equipos.id", ondelete="CASCADE"), index=True
    )
    organizacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizaciones.id"), nullable=True, index=True
    )
    clasificacion: Mapped[str] = mapped_column(String(30), default="normal")
    probabilidad: Mapped[float] = mapped_column(Float, default=0.0)
    modelo_version: Mapped[str] = mapped_column(String(30), default="rf-mvp")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
