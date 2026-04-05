"""Validaciones simples de sensores."""


def is_temperature_valid(value: float) -> bool:
    """Valida un rango razonable de temperatura."""

    return -20.0 <= value <= 120.0


def is_vibration_valid(value: float) -> bool:
    """Valida un rango razonable de vibración."""

    return 0.0 <= value <= 20.0
