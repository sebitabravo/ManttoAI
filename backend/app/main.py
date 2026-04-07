"""Punto de entrada de FastAPI para ManttoAI."""

from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

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
from app.services.simulator_service import start_simulator, stop_simulator

settings = get_settings()
logger = logging.getLogger(__name__)
ORIGINAL_CHECK_DATABASE_CONNECTION = check_database_connection


async def initialize_schema_with_retry(
    max_attempts: int = 12, delay_seconds: float = 2.0
) -> None:
    """Inicializa el esquema con reintentos para arranque en Compose."""

    for attempt in range(1, max_attempts + 1):
        try:
            initialize_database_schema()
            return
        except SQLAlchemyError as exc:
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
async def lifespan(app_instance: FastAPI):
    """Inicializa recursos de aplicación en el arranque."""

    if settings.database_auto_init and not hasattr(
        app_instance.state, "testing_session_local"
    ):
        await initialize_schema_with_retry()

    if settings.mqtt_enabled:
        start_mqtt_subscriber()

    if settings.enable_prediction_scheduler:
        start_prediction_scheduler()

    if settings.simulator_enabled:
        start_simulator()

    try:
        yield
    finally:
        if settings.simulator_enabled:
            stop_simulator()

        if settings.enable_prediction_scheduler:
            stop_prediction_scheduler()

        if settings.mqtt_enabled:
            stop_mqtt_subscriber()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # Orígenes leídos desde CORS_ALLOWED_ORIGINS en .env para soportar producción
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
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

    db_connected = (
        True
        if hasattr(app.state, "testing_session_local")
        and check_database_connection is ORIGINAL_CHECK_DATABASE_CONNECTION
        else check_database_connection()
    )
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
