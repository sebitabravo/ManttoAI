"""Modelo de lectura de sensores."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.organizacion import Organizacion


class Lectura(Base):
    """Representa una lectura telemétrica de un equipo."""

    __tablename__ = "lecturas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id", ondelete="CASCADE"), index=True)
    temperatura: Mapped[float] = mapped_column(Float)
    humedad: Mapped[float] = mapped_column(Float)
    vib_x: Mapped[float] = mapped_column(Float)
    vib_y: Mapped[float] = mapped_column(Float)
    vib_z: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Multi-tenancy
    organizacion_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("organizaciones.id"), nullable=True, default=None
    )

    # Relación a organización (multi-tenancy)
    organizacion: Mapped["Organizacion | None"] = relationship("Organizacion")
