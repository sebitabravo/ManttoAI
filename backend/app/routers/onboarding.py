"""Endpoints del wizard de onboarding."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
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
def get_onboarding_status(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico")),
) -> OnboardingStatusResponse:
    """Retorna el estado actual del onboarding del usuario autenticado."""

    # current_user ya es el usuario de la DB (from require_role dependency)
    return OnboardingStatusResponse(
        onboarding_step=current_user.onboarding_step,
        onboarding_completed=current_user.onboarding_completed,
    )


@router.patch("/step")
def update_onboarding_step(
    payload: OnboardingStepUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico")),
) -> OnboardingStatusResponse:
    """Actualiza el paso actual del onboarding del usuario."""

    # current_user ya es el usuario de la DB

    # Validar que no esté completado
    if usuario.onboarding_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El onboarding ya está completado",
        )

    # Validar secuencia de pasos: no puede saltar más de 1 paso
    current_step = current_user.onboarding_step or 1
    new_step = payload.step
    if abs(new_step - current_step) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No puedes saltar pasos. current_step={current_step}",
        )

    # Actualizar paso
    current_user.onboarding_step = payload.step
    db.commit()
    db.refresh(current_user)

    return OnboardingStatusResponse(
        onboarding_step=current_user.onboarding_step,
        onboarding_completed=current_user.onboarding_completed,
    )


@router.post("/complete", status_code=status.HTTP_204_NO_CONTENT)
def complete_onboarding(
    payload: OnboardingCompleteRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin", "tecnico")),
) -> None:
    """Marca el onboarding como completado y registra los recursos creados."""

    # Validar que el equipo existe y pertenece al usuario u organización
    if payload.equipo_id is not None:
        from app.models.equipo import Equipo

        equipo = db.get(Equipo, payload.equipo_id)
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado"
            )
        # Validar propiedad: equipo debe ser de la organización del usuario o sin organización (propio/global)
        user_org_id = getattr(current_user, "organizacion_id", None)
        if equipo.organizacion_id is not None and equipo.organizacion_id != user_org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para usar este equipo",
            )

    # Marcar como completado
    current_user.onboarding_step = None
    current_user.onboarding_completed = True
    db.commit()


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_onboarding(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin")),
) -> None:
    """Resetea el onboarding para permitir repetir el wizard (solo admin)."""

    # Reiniciar estado del wizard
    current_user.onboarding_step = 1
    current_user.onboarding_completed = False
    db.commit()
