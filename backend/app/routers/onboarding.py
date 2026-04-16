"""Endpoints del wizard de onboarding."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.middleware.rate_limit import limiter
from app.models.usuario import Usuario
from app.schemas.onboarding import (
    OnboardingCompleteRequest,
    OnboardingStatusResponse,
    OnboardingStepUpdate,
)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get(
    "/status",
    response_model=OnboardingStatusResponse,
)
@limiter.limit("60/minute")
def get_onboarding_status(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico")),
) -> OnboardingStatusResponse:
    """Retorna el estado actual del onboarding del usuario autenticado."""

    # Recargar usuario desde la DB para obtener datos frescos
    usuario = db.get(Usuario, current_user.id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    return OnboardingStatusResponse(
        onboarding_step=usuario.onboarding_step,
        onboarding_completed=usuario.onboarding_completed,
    )


@router.patch("/step")
@limiter.limit("30/minute")
def update_onboarding_step(
    payload: OnboardingStepUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico")),
) -> OnboardingStatusResponse:
    """Actualiza el paso actual del onboarding del usuario."""

    # Recargar usuario desde la DB
    usuario = db.get(Usuario, current_user.id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Validar que no esté completado
    if usuario.onboarding_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El onboarding ya está completado",
        )

    # Actualizar paso
    usuario.onboarding_step = payload.step
    db.commit()
    db.refresh(usuario)

    return OnboardingStatusResponse(
        onboarding_step=usuario.onboarding_step,
        onboarding_completed=usuario.onboarding_completed,
    )


@router.post("/complete", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def complete_onboarding(
    payload: OnboardingCompleteRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico")),
) -> None:
    """Marca el onboarding como completado y registra los recursos creados."""

    # Recargar usuario desde la DB
    usuario = db.get(Usuario, current_user.id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Validar que el equipo existe solo si se proporcionó uno
    if payload.equipo_id is not None:
        from app.models.equipo import Equipo

        equipo = db.get(Equipo, payload.equipo_id)
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado"
            )

    # Marcar como completado
    usuario.onboarding_step = None
    usuario.onboarding_completed = True
    db.commit()

    # Nota: En una implementación futura, aquí se podría crear un registro
    # de auditoría para registrar que el usuario completó el onboarding con
    # éxito y qué recursos creó (equipo, API key, etc.)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def reset_onboarding(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> None:
    """Resetea el onboarding para permitir repetir el wizard (solo admin)."""

    usuario = db.get(Usuario, current_user.id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Reiniciar estado del wizard
    usuario.onboarding_step = 1
    usuario.onboarding_completed = False
    db.commit()
