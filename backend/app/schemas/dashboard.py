"""Schemas del contrato de resumen para dashboard."""

from pydantic import BaseModel


class DashboardEquipoResumen(BaseModel):
    """Representa el resumen de un equipo para tarjetas del dashboard."""

    id: int
    nombre: str
    rubro: str
    ultima_temperatura: float | None = None
    ultima_probabilidad: float | None = None
    # Clasificación de la última predicción para el indicador visual del frontend
    ultima_clasificacion: str | None = None
    alertas_activas: int


class DashboardResumenResponse(BaseModel):
    """Contrato estable de respuesta para `GET /dashboard/resumen`."""

    total_equipos: int
    alertas_activas: int
    equipos_en_riesgo: int
    ultima_clasificacion: str
    probabilidad_falla: float
    equipos: list[DashboardEquipoResumen]
