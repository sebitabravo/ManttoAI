"""Regresiones del wiring de credenciales MQTT en los targets Make."""

from pathlib import Path


MAKEFILE_PATH = Path(__file__).resolve().parents[2] / "Makefile"


def test_make_simulate_lee_credenciales_desde_el_contenedor():
    """Los targets MQTT no deben usar defaults del shell host para autenticarse."""

    source = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "docker compose exec backend sh -c" in source
    assert '"$$MQTT_USERNAME"' in source
    assert '"$$MQTT_PASSWORD"' in source
