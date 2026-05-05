"""Punto de entrada de FastAPI para ManttoAI."""

from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.utils.logging_config import setup_logging
from app.database import check_database_connection, initialize_database_schema
from app.dependencies import get_current_user, require_role
from app.middleware.audit import audit_middleware
from app.middleware.rate_limit import setup_rate_limiting
from app.routers import (
    alertas,
    api_keys,
    audit_logs,
    auth,
    dashboard,
    equipos,
    iot,
    lecturas,
    legal,
    mantenciones,
    metrics,
    onboarding,
    predicciones,
    reportes,
    umbrales,
    usuarios,
    chat,
)
from app.services.mqtt_service import start_mqtt_subscriber, stop_mqtt_subscriber
from app.services.prediccion_scheduler_service import (
    start_prediction_scheduler,
    stop_prediction_scheduler,
)
from app.services.simulator_service import start_simulator, stop_simulator

settings = get_settings()
setup_logging(app_name=settings.app_name, level="INFO")
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
API_V1_PREFIX = "/api/v1"


def include_router_with_legacy_support(router, *, dependencies=None) -> None:
    """Expone rutas en /api/v1 y también en raíz por compatibilidad."""

    if dependencies is None:
        app.include_router(router, prefix=API_V1_PREFIX)
        app.include_router(router, include_in_schema=False)
        return

    app.include_router(router, prefix=API_V1_PREFIX, dependencies=dependencies)
    app.include_router(router, dependencies=dependencies, include_in_schema=False)


app.add_middleware(
    CORSMiddleware,
    # Orígenes leídos desde CORS_ALLOWED_ORIGINS en .env para soportar producción
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-API-Key",
        "X-CSRF-Token",
    ],
    expose_headers=["Content-Disposition"],
)

# Configurar rate limiting para protección contra abuso
setup_rate_limiting(app)

# Configurar audit logging automático
app.middleware("http")(audit_middleware)

# Auth expuesto en /api/v1 y raíz por compatibilidad con clientes legacy.
include_router_with_legacy_support(auth.router)
app.include_router(legal.router)  # Documentación legal pública

# Router IoT (público pero con API key authentication)
app.include_router(iot.router, prefix=API_V1_PREFIX)

# Admin-only routers
app.include_router(
    usuarios.router,
    dependencies=[Depends(require_role("admin"))],
    prefix=API_V1_PREFIX,
)
app.include_router(
    api_keys.router,
    dependencies=[Depends(require_role("admin"))],
    prefix=API_V1_PREFIX,
)
app.include_router(
    audit_logs.router,
    dependencies=[Depends(require_role("admin"))],
    prefix=API_V1_PREFIX,
)

# Routers existentes con RBAC aplicado directamente en cada router
# Se exponen también en raíz por compatibilidad con test suite legado.
include_router_with_legacy_support(onboarding.router)
include_router_with_legacy_support(equipos.router)
include_router_with_legacy_support(lecturas.router)
include_router_with_legacy_support(alertas.router)
include_router_with_legacy_support(predicciones.router)
include_router_with_legacy_support(mantenciones.router)
include_router_with_legacy_support(umbrales.router)
include_router_with_legacy_support(dashboard.router)
include_router_with_legacy_support(reportes.router)
include_router_with_legacy_support(chat.router)

# Métricas (requiere auth)
app.include_router(
    metrics.router,
    dependencies=[Depends(get_current_user)],
    prefix=API_V1_PREFIX,
)


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
