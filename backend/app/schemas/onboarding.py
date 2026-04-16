"""Schemas de onboarding."""

from pydantic import BaseModel, Field, field_validator


class OnboardingStatusResponse(BaseModel):
    """Estado actual del onboarding de un usuario."""

    onboarding_step: int | None = Field(
        default=None,
        description="Paso actual del wizard (1-5), None si está completado",
    )
    onboarding_completed: bool = Field(
        default=False,
        description="Indica si el usuario completó el wizard",
    )


class OnboardingStepUpdate(BaseModel):
    """Payload para actualizar el paso actual del onboarding."""

    step: int = Field(
        ge=1,
        le=5,
        description="Paso actual del wizard (1-5)",
    )

    @field_validator("step")
    def validate_step(cls, value: int) -> int:
        """Valida que el paso esté en el rango válido."""

        if value < 1 or value > 5:
            raise ValueError("step debe estar entre 1 y 5")
        return value


class OnboardingCompleteRequest(BaseModel):
    """Payload para marcar el onboarding como completado."""

    equipo_id: int | None = Field(
        default=None,
        description="ID del equipo creado durante el onboarding (None si el usuario saltó el wizard)",
    )
    api_key_id: int | None = Field(
        default=None,
        description="ID de la API key creada durante el onboarding (opcional)",
    )
