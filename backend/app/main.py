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
from app.middleware.rate_limit import setup_rate_limiting
from app.routers import (
    alertas,
    api_keys,
    audit_logs,
    auth,
    chat,
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

# Entornos donde se aplican medidas de seguridad completas
NON_DEV_ENVS = {"staging", "stage", "production", "prod"}
IS_PROD = settings.app_env.strip().lower() in NON_DEV_ENVS


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


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    # VULN-01: Deshabilitar documentación OpenAPI pública en producción
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    openapi_url=None if IS_PROD else "/openapi.json",
)
API_V1_PREFIX = "/api/v1"


def include_router_v1(router, *, dependencies=None) -> None:
    """Expone rutas exclusivamente bajo /api/v1 (sin duplicación legacy)."""
    app.include_router(router, prefix=API_V1_PREFIX, dependencies=dependencies)


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

# VULN-02 + SEC-05: Middleware de headers de seguridad
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Añade headers de seguridad recomendados por OWASP a cada respuesta."""
    response: Response = await call_next(request)

    if IS_PROD:
        # HSTS: solo en producción con HTTPS
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "0"  # Obsoleto pero bloquea reflejado en navegadores viejos
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), interest-cohort=()"
    )
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

    return response


# OBS-01: Middleware de métricas de request
@app.middleware("http")
async def request_metrics_middleware(request: Request, call_next):
    """Registra métricas de cada request HTTP para el endpoint /metrics."""
    from time import perf_counter
    from app.routers.metrics import _record_metrics

    start = perf_counter()
    response = await call_next(request)
    duration = perf_counter() - start
    # Usar la ruta como identificador de endpoint (sin query params)
    endpoint = f"{request.method} {request.url.path}"
    _record_metrics(endpoint, duration)
    return response


# Configurar rate limiting para protección contra abuso
setup_rate_limiting(app)

# Configurar audit logging automático
app.middleware("http")(audit_middleware)

# Auth: expuesto en /api/v1 y también en raíz para OAuth2PasswordBearer tokenUrl.
# OAuth2PasswordBearer espera /auth/login en Swagger UI.
include_router_v1(auth.router)
app.include_router(auth.router, include_in_schema=False)
app.include_router(legal.router)  # Documentación legal pública (rutas propias)

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

# ARCH-01: Rutas de dominio solo bajo /api/v1 (sin duplicación legacy)
include_router_v1(onboarding.router)
include_router_v1(equipos.router)
include_router_v1(lecturas.router)
include_router_v1(alertas.router)
include_router_v1(predicciones.router)
include_router_v1(mantenciones.router)
include_router_v1(umbrales.router)
include_router_v1(dashboard.router)
include_router_v1(reportes.router)
include_router_v1(chat.router)

# Métricas (requiere auth)
app.include_router(
    metrics.router,
    dependencies=[Depends(get_current_user)],
    prefix=API_V1_PREFIX,
)


@app.get("/health", tags=["system"])
def health_check() -> JSONResponse:
    """Health check que verifica DB, Redis y MQTT."""

    components: dict[str, str] = {}

    # Database
    db_connected = (
        True
        if hasattr(app.state, "testing_session_local")
        and check_database_connection is ORIGINAL_CHECK_DATABASE_CONNECTION
        else check_database_connection()
    )
    components["database"] = "ok" if db_connected else "error"

    # Redis
    redis_ok = False
    try:
        import redis as redis_lib

        r = redis_lib.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password or None,
            socket_connect_timeout=1,
        )
        redis_ok = r.ping()
    except Exception:
        pass
    components["redis"] = "ok" if redis_ok else "error"

    # MQTT broker
    mqtt_ok = False
    if settings.mqtt_enabled:
        try:
            import socket

            sock = socket.create_connection(
                (settings.mqtt_broker_host, settings.mqtt_broker_port), timeout=2
            )
            sock.close()
            mqtt_ok = True
        except Exception:
            pass
    else:
        mqtt_ok = True  # No requerido si está deshabilitado
    components["mqtt"] = "ok" if mqtt_ok else "error"

    all_ok = all(v == "ok" for v in components.values())
    status_code = 200 if all_ok else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if all_ok else "degraded",
            "components": components,
        },
    )
