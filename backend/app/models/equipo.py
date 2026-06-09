"""Modelo de equipo."""

from datetime import datetime

from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.organizacion import Organizacion


class Equipo(Base):
    """
    Representa un equipo monitoreado.

    Multi-tenancy (RNF-28):
    `organizacion_id` es FK a organizaciones, nullable para compatibilidad
    con datos existentes. Todos los queries deben filtrar por
    `organizacion_id` del usuario autenticado.
    """

    __tablename__ = "equipos"
    __table_args__ = (
        CheckConstraint(
            "rubro IN ('industrial', 'agricola', 'comercial')",
            name="ck_equipos_rubro_valido",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    ubicacion: Mapped[str] = mapped_column(String(120), default="Laboratorio")
    tipo: Mapped[str] = mapped_column(String(80), default="Motor")
    rubro: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        default="industrial",
    )
    descripcion: Mapped[str] = mapped_column(
        String(255),
        default="Equipo monitoreado por ManttoAI",
    )
    estado: Mapped[str] = mapped_column(String(30), default="operativo")
    mac_address: Mapped[str | None] = mapped_column(
        String(17), unique=True, index=True, nullable=True
    )
    # Organización a la que pertenece el equipo (multi-tenancy).
    organizacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizaciones.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relaciones
    organizacion: Mapped[Optional["Organizacion"]] = relationship(
        "Organizacion", back_populates="equipos"
    )
