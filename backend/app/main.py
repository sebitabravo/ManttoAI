"""Punto de entrada de FastAPI para ManttoAI."""

from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.utils.logging_config import setup_logging
from app.database import check_database_connection, initialize_database_schema
from app.dependencies import get_current_user, require_role
from app.middleware.audit import audit_middleware
from app.middleware.correlation import CorrelationMiddleware
from app.middleware.rate_limit import setup_rate_limiting
from app.middleware.request_metrics import RequestMetricsMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.tenant import TenantMiddleware
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


# Ocultar documentación OpenAPI en producción (VULN-01)
_docs_enabled = settings.app_env not in {"production", "staging", "prod"}

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)
API_V1_PREFIX = "/api/v1"


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

# Security headers (OWASP recomendados)
app.add_middleware(SecurityHeadersMiddleware)

# Correlation ID para trazabilidad de requests
app.add_middleware(CorrelationMiddleware)

# Tenant identification via X-Tenant-ID header
app.add_middleware(TenantMiddleware)

# Configurar rate limiting para protección contra abuso
setup_rate_limiting(app)

# Métricas de latencia por request
app.add_middleware(RequestMetricsMiddleware)

# Configurar audit logging automático
app.middleware("http")(audit_middleware)

# Auth expuesto en /api/v1 y raíz por compatibilidad con clientes legacy
app.include_router(auth.router)
app.include_router(auth.router, prefix=API_V1_PREFIX)

# Documentación legal pública
app.include_router(legal.router)

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

# Domain routers — solo /api/v1
app.include_router(onboarding.router, prefix=API_V1_PREFIX)
app.include_router(equipos.router, prefix=API_V1_PREFIX)
app.include_router(lecturas.router, prefix=API_V1_PREFIX)
app.include_router(alertas.router, prefix=API_V1_PREFIX)
app.include_router(predicciones.router, prefix=API_V1_PREFIX)
app.include_router(mantenciones.router, prefix=API_V1_PREFIX)
app.include_router(umbrales.router, prefix=API_V1_PREFIX)
app.include_router(dashboard.router, prefix=API_V1_PREFIX)
app.include_router(reportes.router, prefix=API_V1_PREFIX)
app.include_router(chat.router, prefix=API_V1_PREFIX)

# Métricas (requiere auth)
app.include_router(
    metrics.router,
    dependencies=[Depends(get_current_user)],
    prefix=API_V1_PREFIX,
)


@app.get("/health", tags=["system"])
async def health_check() -> JSONResponse:
    """Health check con verificación de DB, Redis y MQTT."""

    import os

    components = {"db": False, "redis": False, "mqtt": False}

    # Verificar base de datos
    try:
        db_connected = (
            check_database_connection()
            if check_database_connection is not ORIGINAL_CHECK_DATABASE_CONNECTION
            or not hasattr(app.state, "testing_session_local")
            else True
        )
        components["db"] = True if db_connected else False
    except Exception:
        components["db"] = False

    # Verificar Redis si está configurado
    redis_url = os.getenv("REDIS_URL", "")
    redis_password = os.getenv("REDIS_PASSWORD", "")
    if redis_url:
        try:
            import redis

            # redis.from_url no incluye password si no viene en la URL.
            # Con requirepass activo, el ping sin auth falla aunque Redis funcione.
            if redis_password:
                r = redis.Redis(
                    host=os.getenv("REDIS_HOST", "redis"),
                    port=int(os.getenv("REDIS_PORT", "6379")),
                    password=redis_password,
                    socket_connect_timeout=2,
                )
            else:
                r = redis.from_url(redis_url, socket_connect_timeout=2)
            r.ping()
            components["redis"] = True
        except Exception:
            components["redis"] = False
    else:
        components["redis"] = True  # No configurado = no requerido

    # Verificar MQTT si está habilitado
    if settings.mqtt_enabled:
        try:
            import socket

            mqtt_host = os.getenv("MQTT_BROKER_HOST", "mosquitto")
            mqtt_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((mqtt_host, mqtt_port))
            sock.close()
            components["mqtt"] = result == 0
        except Exception:
            components["mqtt"] = False
    else:
        components["mqtt"] = True  # No habilitado = no requerido

    all_healthy = all(components.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if all_healthy else "degraded",
            "components": components,
        },
    )
