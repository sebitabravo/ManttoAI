"""Servicios de alertas y umbrales."""

from datetime import datetime, timezone

from app.schemas.alerta import AlertaResponse
from app.schemas.lectura import LecturaResponse


def evaluate_thresholds(lectura: LecturaResponse) -> list[AlertaResponse]:
    """Evalúa reglas simples de alerta para el scaffold."""

    alertas: list[AlertaResponse] = []
    if lectura.temperatura > 50:
        alertas.append(
            AlertaResponse(
                id=1,
                equipo_id=lectura.equipo_id,
                tipo="temperatura",
                mensaje="Temperatura fuera de rango",
                nivel="alto",
                email_enviado=False,
                leida=False,
                created_at=datetime.now(timezone.utc),
            )
        )
    return alertas


def list_alertas() -> list[AlertaResponse]:
    """Entrega alertas activas demo."""

    lectura_demo = LecturaResponse(
        id=1,
        equipo_id=1,
        temperatura=51.2,
        humedad=60.0,
        vib_x=0.4,
        vib_y=0.2,
        vib_z=9.8,
        timestamp=datetime.now(timezone.utc),
    )
    return evaluate_thresholds(lectura_demo)


def mark_as_read(alerta_id: int) -> dict[str, int | bool]:
    """Marca una alerta demo como leída."""

    return {"id": alerta_id, "leida": True}
