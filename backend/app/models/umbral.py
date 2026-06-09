"""Modelo de umbral."""

from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Umbral(Base):
    """Representa los límites aceptables de una variable monitoreada."""

    __tablename__ = "umbrales"
    __table_args__ = (
        UniqueConstraint("equipo_id", "variable", name="uq_umbral_equipo_variable"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    equipo_id: Mapped[int] = mapped_column(
        ForeignKey("equipos.id", ondelete="CASCADE"), index=True
    )
    organizacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizaciones.id"), nullable=True, index=True
    )
    variable: Mapped[str] = mapped_column(String(50))
    valor_min: Mapped[float] = mapped_column(Float, default=0.0)
    valor_max: Mapped[float] = mapped_column(Float, default=100.0)
