"""Configuración de SQLAlchemy para el proyecto."""

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos."""


settings = get_settings()

connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def initialize_database_schema() -> None:
    """Crea las tablas faltantes del esquema para el MVP."""

    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def check_database_connection() -> bool:
    """Verifica conectividad básica de base de datos con un SELECT 1."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as exc:
        logger.warning("No se pudo conectar a la base de datos: %s", exc)
        return False
