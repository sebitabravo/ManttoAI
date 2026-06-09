"""Modelo de organización para multi-tenancy."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.equipo import Equipo
    from app.models.usuario import Usuario


class Organizacion(Base):
    """Representa una organización (tenant) en el sistema multi-tenancy."""

    __tablename__ = "organizaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    rubro: Mapped[str] = mapped_column(String(30), default="industrial")
    plan_id: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relaciones
    usuarios: Mapped[list["Usuario"]] = relationship(  # noqa: F821
        "Usuario", back_populates="organizacion"
    )
    equipos: Mapped[list["Equipo"]] = relationship(  # noqa: F821
        "Equipo", back_populates="organizacion"
    )
