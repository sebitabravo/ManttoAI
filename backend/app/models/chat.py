"""Modelo para Historial de Chat."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class MensajeChat(Base):
    """Guarda el historial de interacciones con el Asistente de IA."""

    __tablename__ = "mensajes_chat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    mensaje_usuario: Mapped[str] = mapped_column(Text, nullable=False)
    respuesta_ia: Mapped[str] = mapped_column(Text, nullable=False)
    fuente: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relación para acceder al usuario desde el mensaje
    usuario: Mapped["Usuario"] = relationship()
