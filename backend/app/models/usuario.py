"""Modelo de usuario."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.organizacion import Organizacion


class Usuario(Base):
    """Representa un usuario autenticable."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(30), default="visualizador")
    telefono: Mapped[str | None] = mapped_column(
        String(30), nullable=True, default=None
    )
    # Avatar seleccionado por el usuario (nombre del icono/emoji)
    avatar: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
    organizacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizaciones.id"), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # Campos para el wizard de onboarding (RNF-26)
    # onboarding_step: paso actual del wizard (1-5), null si completado
    # Constraint a nivel DB para garantizar integridad (nullable permite null cuando已完成)
    onboarding_step: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=1,
        comment="Paso actual del wizard (1-5), null si completado",
    )
    # onboarding_completed: flag que indica si el usuario completó el wizard
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relaciones
    organizacion: Mapped[Optional["Organizacion"]] = relationship(
        "Organizacion", back_populates="usuarios"
    )
