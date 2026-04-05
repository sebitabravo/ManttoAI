"""Routers disponibles del backend."""

from app.routers import (
    alertas,
    auth,
    dashboard,
    equipos,
    lecturas,
    mantenciones,
    predicciones,
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
]
