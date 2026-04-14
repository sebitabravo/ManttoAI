"""Modelo de equipo."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Equipo(Base):
    """
    Representa un equipo monitoreado.

    Diseño multi-tenancy (RNF-28):
    El campo `organizacion_id` es el punto de extensión para migración a
    multi-tenant. En el MVP es nullable (single-tenant). Para habilitar
    multi-tenancy completo, agregar FK a tabla `organizaciones` y filtrar
    todos los queries por `organizacion_id` del usuario autenticado.
    """

    __tablename__ = "equipos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    ubicacion: Mapped[str] = mapped_column(String(120), default="Laboratorio")
    tipo: Mapped[str] = mapped_column(String(80), default="Motor")
    descripcion: Mapped[str] = mapped_column(
        String(255),
        default="Equipo monitoreado por ManttoAI",
    )
    estado: Mapped[str] = mapped_column(String(30), default="operativo")
    # Punto de extensión para multi-tenancy (RNF-28).
    # Nullable en MVP single-tenant. Para multi-tenant: agregar FK a organizaciones.
    organizacion_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
