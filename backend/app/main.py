"""Punto de entrada de FastAPI para ManttoAI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
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

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(equipos.router)
app.include_router(lecturas.router)
app.include_router(alertas.router)
app.include_router(predicciones.router)
app.include_router(mantenciones.router)
app.include_router(umbrales.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Entrega el estado mínimo de salud de la API."""

    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }
