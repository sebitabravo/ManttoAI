"""Helpers comunes para servicios con acceso a base de datos."""

from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

EntityT = TypeVar("EntityT")


def get_entity_or_404(
    db: Session,
    model_class: type[EntityT],
    entity_id: int,
    detail: str,
) -> EntityT:
    """Obtiene una entidad por id o retorna HTTP 404."""

    entity = db.get(model_class, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return entity
