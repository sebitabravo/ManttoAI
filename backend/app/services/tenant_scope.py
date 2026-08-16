"""Utilidades de alcance por organización para consultas de dominio."""

from typing import Any

from sqlalchemy import ColumnElement
from sqlalchemy.orm import Session

# Un servicio invocado por un worker interno puede necesitar ver todos los
# tenants; una petición autenticada siempre reemplaza este sentinel en db.info.
UNSCOPED = object()


def resolve_organization_id(
    db: Session, organization_id: int | None | object = UNSCOPED
) -> int | None | object:
    """Resuelve el tenant explícito o el asociado a la sesión de la petición."""

    if organization_id is not UNSCOPED:
        return organization_id
    return db.info.get("organizacion_id", UNSCOPED)


def organization_clause(
    column: ColumnElement[Any], organization_id: int | None | object
) -> ColumnElement[bool] | None:
    """Construye una condición segura para IDs de organización nullable."""

    if organization_id is UNSCOPED:
        return None
    if organization_id is None:
        return column.is_(None)
    return column == organization_id


def add_organization_scope(
    query: Any,
    column: ColumnElement[Any],
    db: Session,
    organization_id: int | None | object = UNSCOPED,
) -> Any:
    """Aplica alcance a una query, manteniendo workers internos sin restricción."""

    resolved_id = resolve_organization_id(db, organization_id)
    clause = organization_clause(column, resolved_id)
    return query.where(clause) if clause is not None else query
