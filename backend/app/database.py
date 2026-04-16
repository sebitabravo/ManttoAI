"""Configuración de SQLAlchemy para el proyecto."""

import logging
from os import getenv

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos."""


settings = get_settings()

connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

# Optimización para 50 usuarios concurrentes
engine = create_engine(
    settings.database_url,
    future=True,
    connect_args=connect_args,
    pool_size=20,  # Número de conexiones permanentes
    max_overflow=30,  # Conexiones adicionales en picos de carga
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_recycle=3600,  # Reciclar conexiones cada hora
    echo=False,  # No loguear queries en producción
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def initialize_database_schema() -> None:
    """Crea las tablas faltantes del esquema para el MVP."""

    from app import models  # noqa: F401

    if should_auto_create_schema():
        Base.metadata.create_all(bind=engine)
    else:
        logger.info(
            "Se omitió auto create_all de esquema. "
            "Definí ALLOW_SCHEMA_AUTO_CREATE=true para habilitarlo explícitamente"
        )

    if should_apply_runtime_schema_fixes():
        apply_runtime_schema_fixes()
    else:
        logger.info(
            "Se omitieron runtime schema fixes. "
            "Definí ALLOW_RUNTIME_SCHEMA_CHANGES=true para habilitarlos explícitamente"
        )


def should_auto_create_schema() -> bool:
    """Define si create_all puede ejecutarse automáticamente."""

    if not settings.database_auto_init:
        return False

    app_env = settings.app_env.strip().lower()
    if app_env in {"development", "dev"}:
        return True

    allow_auto_create = getenv("ALLOW_SCHEMA_AUTO_CREATE", "false")
    return allow_auto_create.strip().lower() in {"1", "true", "yes"}


def should_apply_runtime_schema_fixes() -> bool:
    """Define si los parches runtime de esquema deben ejecutarse."""

    if not settings.database_auto_init:
        return False

    app_env = settings.app_env.strip().lower()
    if app_env in {"development", "dev"}:
        return True

    allow_runtime_changes = getenv("ALLOW_RUNTIME_SCHEMA_CHANGES", "false")
    return allow_runtime_changes.strip().lower() in {"1", "true", "yes"}


def _list_table_columns(table_name: str) -> set[str]:
    """Retorna columnas disponibles en una tabla del esquema actual."""

    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return {str(column["name"]) for column in columns}


def _add_column_if_missing(table_name: str, column_name: str, ddl: str) -> bool:
    """Agrega una columna si no existe; retorna True cuando aplica cambios."""

    existing_columns = _list_table_columns(table_name)
    if column_name in existing_columns:
        return False

    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {ddl}"))
    return True


def _dedupe_alertas_by_logical_key() -> int:
    """Elimina alertas duplicadas por (equipo_id, tipo, mensaje)."""

    dialect = engine.dialect.name
    with engine.begin() as connection:
        if dialect == "mysql":
            result = connection.execute(
                text(
                    """
                    DELETE a1
                    FROM alertas a1
                    INNER JOIN alertas a2
                        ON a1.equipo_id = a2.equipo_id
                        AND a1.tipo = a2.tipo
                        AND a1.mensaje = a2.mensaje
                        AND a1.id > a2.id
                    """
                )
            )
            return int(getattr(result, "rowcount", 0) or 0)

        if dialect == "sqlite":
            result = connection.execute(
                text(
                    """
                    DELETE FROM alertas
                    WHERE id NOT IN (
                        SELECT MIN(id)
                        FROM alertas
                        GROUP BY equipo_id, tipo, mensaje
                    )
                    """
                )
            )
            return int(getattr(result, "rowcount", 0) or 0)

        return 0


def _ensure_alerta_unique_index() -> bool:
    """Elimina índice único legacy de alertas si todavía existe."""

    index_name = "uq_alerta_activa_por_equipo_tipo_mensaje"

    inspector = inspect(engine)
    indexes = inspector.get_indexes("alertas")
    constraints = inspector.get_unique_constraints("alertas")

    index_exists = False
    for index in indexes:
        if index.get("name") == index_name:
            index_exists = True
            break

    if not index_exists:
        for constraint in constraints:
            if constraint.get("name") == index_name:
                index_exists = True
                break

    if not index_exists:
        return False

    dialect = engine.dialect.name
    with engine.begin() as connection:
        try:
            if dialect == "mysql":
                connection.execute(text(f"ALTER TABLE alertas DROP INDEX {index_name}"))
            else:
                connection.execute(text(f"DROP INDEX IF EXISTS {index_name}"))
        except SQLAlchemyError:
            logger.debug("No se pudo eliminar índice único legacy de alertas")
            return False

    return True


def apply_runtime_schema_fixes() -> None:
    """Aplica parches idempotentes de esquema para compatibilidad de demo."""

    try:
        equipo_changed = _add_column_if_missing(
            "equipos",
            "descripcion",
            "descripcion VARCHAR(255) NOT NULL DEFAULT 'Equipo monitoreado por ManttoAI'",
        )
        equipo_org_changed = _add_column_if_missing(
            "equipos",
            "organizacion_id",
            "organizacion_id INTEGER NULL DEFAULT NULL",
        )
        mantencion_programada_changed = _add_column_if_missing(
            "mantenciones",
            "fecha_programada",
            "fecha_programada DATETIME NULL",
        )
        mantencion_ejecucion_changed = _add_column_if_missing(
            "mantenciones",
            "fecha_ejecucion",
            "fecha_ejecucion DATETIME NULL",
        )
        usuario_active_changed = _add_column_if_missing(
            "usuarios",
            "is_active",
            "is_active BOOLEAN NOT NULL DEFAULT 1",
        )
        usuario_password_changed_changed = _add_column_if_missing(
            "usuarios",
            "password_changed_at",
            "password_changed_at DATETIME NULL",
        )
        usuario_onboarding_step_changed = _add_column_if_missing(
            "usuarios",
            "onboarding_step",
            "onboarding_step INTEGER NULL DEFAULT 1",
        )
        usuario_onboarding_completed_changed = _add_column_if_missing(
            "usuarios",
            "onboarding_completed",
            "onboarding_completed BOOLEAN NOT NULL DEFAULT 0",
        )
        usuario_telefono_changed = _add_column_if_missing(
            "usuarios",
            "telefono",
            "telefono VARCHAR(30) NULL DEFAULT NULL",
        )
        usuario_avatar_changed = _add_column_if_missing(
            "usuarios",
            "avatar",
            "avatar VARCHAR(50) NULL DEFAULT NULL",
        )
        alerta_index_changed = _ensure_alerta_unique_index()

        if any(
            [
                equipo_changed,
                equipo_org_changed,
                mantencion_programada_changed,
                mantencion_ejecucion_changed,
                usuario_active_changed,
                usuario_password_changed_changed,
                usuario_onboarding_step_changed,
                usuario_onboarding_completed_changed,
                usuario_telefono_changed,
                usuario_avatar_changed,
                alerta_index_changed,
            ]
        ):
            logger.info(
                "Se aplicaron parches de compatibilidad de esquema "
                "(equipos.descripcion=%s, equipos.organizacion_id=%s, "
                "mantenciones.fecha_programada=%s, "
                "mantenciones.fecha_ejecucion=%s, usuarios.is_active=%s, "
                "usuarios.password_changed_at=%s, usuarios.onboarding_step=%s, "
                "usuarios.onboarding_completed=%s, usuarios.telefono=%s, usuarios.avatar=%s, "
                "alerta_unique_index_removed=%s)",
                equipo_changed,
                equipo_org_changed,
                mantencion_programada_changed,
                mantencion_ejecucion_changed,
                usuario_active_changed,
                usuario_password_changed_changed,
                usuario_onboarding_step_changed,
                usuario_onboarding_completed_changed,
                usuario_telefono_changed,
                usuario_avatar_changed,
                alerta_index_changed,
            )
    except (RuntimeError, SQLAlchemyError, DBAPIError):
        logger.exception("Falló la aplicación de parches de compatibilidad de esquema")


def check_database_connection() -> bool:
    """Verifica conectividad básica de base de datos con un SELECT 1."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as exc:
        logger.warning(
            "No se pudo conectar a la base de datos: %s: %s",
            type(exc).__name__,
            str(exc),
        )
        return False
