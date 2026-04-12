"""Endpoints públicos para dispositivos IoT (autenticados con API Key)."""

import hashlib

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.dependencies import get_api_key_user, get_db
from app.middleware.rate_limit import limiter
from app.models.api_key import APIKey
from app.schemas.lectura import LecturaCreate, LecturaResponse
from app.services.lectura_service import create_lectura

router = APIRouter(prefix="/iot", tags=["iot"])


def _resolve_iot_rate_limit_key(request: Request) -> str:
    """Genera clave de rate limit por API key (sin exponer secreto plano)."""

    api_key = request.headers.get("X-API-Key", "").strip()
    if not api_key:
        return "anonymous"

    api_key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    return f"api-key:{api_key_hash}"


@router.post(
    "/lecturas", response_model=LecturaResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("100/minute", key_func=_resolve_iot_rate_limit_key)
def post_lectura_iot(
    request: Request,
    payload: LecturaCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    api_key: APIKey | None = Depends(get_api_key_user),
) -> LecturaResponse:
    """
    Crea una lectura desde un dispositivo IoT autenticado con API Key.

    Autenticación: Header X-API-Key con la key del dispositivo.
    """

    # Validar API key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida o inactiva",
        )

    # Verificar que el dispositivo coincide con el de la API key
    if api_key.device_id != str(payload.equipo_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key no autorizada para este equipo",
        )

    # Crear lectura
    return create_lectura(db, payload, background_tasks=background_tasks)
