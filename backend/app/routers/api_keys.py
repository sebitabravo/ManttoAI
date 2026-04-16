"""Endpoints de gestión de API Keys."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.usuario import Usuario
from app.schemas.api_key import APIKeyCreate, APIKeyDetailResponse, APIKeyResponse
from app.services.api_key_service import (
    create_api_key,
    get_api_key_by_id,
    list_api_keys,
    revoke_api_key,
)

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post(
    "", response_model=APIKeyDetailResponse, status_code=status.HTTP_201_CREATED
)
def create_new_api_key(
    payload: APIKeyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> APIKeyDetailResponse:
    """Crea una nueva API Key para un dispositivo IoT (solo admin)."""

    try:
        api_key, plain_key = create_api_key(
            db, device_id=payload.device_id, created_by_id=current_user.id
        )

        # Retornar con la key completa (solo se muestra una vez)
        return APIKeyDetailResponse(
            id=api_key.id,
            key_prefix=api_key.key_prefix,
            device_id=api_key.device_id,
            is_active=api_key.is_active,
            created_at=api_key.created_at,
            last_used_at=api_key.last_used_at,
            revoked_at=api_key.revoked_at,
            key=plain_key,  # La key completa solo en creación
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("", response_model=list[APIKeyResponse])
def get_api_keys(
    request: Request,
    include_inactive: bool = False,
    device_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> list[APIKeyResponse]:
    """Lista todas las API Keys (solo admin)."""

    api_keys = list_api_keys(db, include_inactive=include_inactive, device_id=device_id)
    return [APIKeyResponse.model_validate(key) for key in api_keys]


@router.get("/{api_key_id}", response_model=APIKeyResponse)
def get_api_key(
    api_key_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> APIKeyResponse:
    """Retorna una API Key por ID (solo admin)."""

    api_key = get_api_key_by_id(db, api_key_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API Key no encontrada"
        )

    return APIKeyResponse.model_validate(api_key)


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    api_key_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> None:
    """Revoca una API Key (solo admin)."""

    try:
        revoke_api_key(db, api_key_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
