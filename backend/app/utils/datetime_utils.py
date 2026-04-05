"""Utilidades de fecha y hora."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Retorna la fecha actual en UTC."""

    return datetime.now(timezone.utc)


def to_iso(value: datetime) -> str:
    """Formatea una fecha a ISO 8601."""

    return value.astimezone(timezone.utc).isoformat()
