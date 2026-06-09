"""Routers disponibles del backend."""

from app.routers import (
    alertas,
    auth,
    billing,
    dashboard,
    equipos,
    lecturas,
    mantenciones,
    predicciones,
    reportes,
    sla,
    umbrales,
)

__all__ = [
    "auth",
    "equipos",
    "lecturas",
    "alertas",
    "predicciones",
    "mantenciones",
    "umbrales",
    "dashboard",
    "reportes",
    "billing",
    "sla",
]
