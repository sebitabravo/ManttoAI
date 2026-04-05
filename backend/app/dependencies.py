"""Dependencias reutilizables de FastAPI."""

from collections.abc import Generator

from app.database import SessionLocal


def get_db() -> Generator:
    """Entrega una sesión de base de datos por request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user() -> dict[str, str]:
    """Retorna un usuario demo mientras se implementa autenticación real."""

    return {"email": "demo@example.com", "rol": "admin"}
