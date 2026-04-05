"""Servicios de apoyo para MQTT."""

import json

from app.config import get_settings


def build_topic(equipo_id: int) -> str:
    """Construye el topic MQTT esperado para un equipo."""

    settings = get_settings()
    return f"{settings.mqtt_base_topic}/{equipo_id}/lecturas"


def parse_message(payload: str) -> dict:
    """Parsea un payload JSON simple recibido por MQTT."""

    return json.loads(payload)
