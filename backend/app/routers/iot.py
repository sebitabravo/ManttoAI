"""Endpoints públicos para dispositivos IoT (autenticados con API Key)."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_api_key_user, get_db
from app.models.api_key import APIKey
from app.schemas.lectura import LecturaCreate, LecturaResponse
from app.services.lectura_service import create_lectura

router = APIRouter(prefix="/iot", tags=["iot"])


@router.post(
    "/lecturas", response_model=LecturaResponse, status_code=status.HTTP_201_CREATED
)
def post_lectura_iot(
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
