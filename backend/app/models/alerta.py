"""Modelo de alerta."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Alerta(Base):
    """Representa una alerta generada por umbrales o predicción."""

    __tablename__ = "alertas"
    __table_args__ = (
        # 'leida' fue removido de la constraint: incluirlo permitía duplicar
        # la misma alerta (una leída + una no leída), lo cual es incorrecto.
        # La deduplicación se hace por equipo/tipo/mensaje sin importar el estado.
        UniqueConstraint(
            "equipo_id",
            "tipo",
            "mensaje",
            name="uq_alerta_activa_por_equipo_tipo_mensaje",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(50))
    mensaje: Mapped[str] = mapped_column(String(255))
    nivel: Mapped[str] = mapped_column(String(20), default="medio")
    email_enviado: Mapped[bool] = mapped_column(Boolean, default=False)
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
