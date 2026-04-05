"""Punto de entrada de FastAPI para ManttoAI."""

from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.dependencies import get_current_user
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
from app.services.prediccion_scheduler_service import (
    start_prediction_scheduler,
    stop_prediction_scheduler,
)

settings = get_settings()
logger = logging.getLogger(__name__)


async def initialize_schema_with_retry(
    max_attempts: int = 12, delay_seconds: float = 2.0
) -> None:
    """Inicializa el esquema con reintentos para arranque en Compose."""

    for attempt in range(1, max_attempts + 1):
        try:
            initialize_database_schema()
            return
        except Exception as exc:
            if attempt >= max_attempts:
                raise

            logger.warning(
                "Base de datos aún no lista para inicializar esquema "
                "(intento %s/%s): %s",
                attempt,
                max_attempts,
                exc,
            )
            await asyncio.sleep(delay_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Inicializa recursos de aplicación en el arranque."""

    if settings.database_auto_init:
        await initialize_schema_with_retry()

    if settings.mqtt_enabled:
        start_mqtt_subscriber()

    if settings.enable_prediction_scheduler:
        start_prediction_scheduler()

    try:
        yield
    finally:
        if settings.enable_prediction_scheduler:
            stop_prediction_scheduler()

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
protected_dependencies = [Depends(get_current_user)]

app.include_router(equipos.router, dependencies=protected_dependencies)
app.include_router(lecturas.router, dependencies=protected_dependencies)
app.include_router(alertas.router, dependencies=protected_dependencies)
app.include_router(predicciones.router, dependencies=protected_dependencies)
app.include_router(mantenciones.router, dependencies=protected_dependencies)
app.include_router(umbrales.router, dependencies=protected_dependencies)
app.include_router(dashboard.router, dependencies=protected_dependencies)


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
