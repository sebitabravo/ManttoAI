"""Modelo de equipo."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Equipo(Base):
    """Representa un equipo monitoreado."""

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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
