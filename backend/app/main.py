"""Punto de entrada de FastAPI para ManttoAI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import check_database_connection, initialize_database_schema
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
from app.services.mqtt_service import start_mqtt_subscriber, stop_mqtt_subscriber

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Inicializa recursos de aplicación en el arranque."""

    if settings.database_auto_init:
        initialize_database_schema()

    if settings.mqtt_enabled:
        start_mqtt_subscriber()

    try:
        yield
    finally:
        if settings.mqtt_enabled:
            stop_mqtt_subscriber()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

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
def health_check() -> JSONResponse:
    """Entrega estado de API y conectividad de base de datos."""

    db_connected = check_database_connection()
    status_code = 200 if db_connected else 503
    status = "ok" if db_connected else "error"

    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "service": settings.app_name,
            "environment": settings.app_env,
            "database": {"connected": db_connected},
        },
    )
