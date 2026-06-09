"""Modelo de mantención."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.organizacion import Organizacion


class Mantencion(Base):
    """Representa una mantención planificada o ejecutada."""

    __tablename__ = "mantenciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id", ondelete="CASCADE"), index=True)
    tipo: Mapped[str] = mapped_column(String(60), default="preventiva")
    descripcion: Mapped[str] = mapped_column(
        String(255), default="Pendiente de definir"
    )
    fecha_programada: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    fecha_ejecucion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    estado: Mapped[str] = mapped_column(String(30), default="programada")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Multi-tenancy
    organizacion_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("organizaciones.id"), nullable=True, default=None
    )

    # Relación a organización (multi-tenancy)
    organizacion: Mapped["Organizacion | None"] = relationship("Organizacion")
