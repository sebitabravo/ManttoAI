"""Modelos SQLAlchemy disponibles para ManttoAI."""

from app.models.alerta import Alerta
from app.models.api_key import APIKey
from app.models.audit_log import AuditLog
from app.models.equipo import Equipo
from app.models.lectura import Lectura
from app.models.mantencion import Mantencion
from app.models.prediccion import Prediccion
from app.models.umbral import Umbral
from app.models.usuario import Usuario
from app.models.chat import MensajeChat
from app.models.organizacion import Organizacion
from app.models.sla import SLAEvent, SLAReport
from app.models.suscripcion import Plan, Suscripcion

__all__ = [
    "Alerta",
    "APIKey",
    "AuditLog",
    "Equipo",
    "Lectura",
    "Mantencion",
    "MensajeChat",
    "Organizacion",
    "Plan",
    "Prediccion",
    "SLAEvent",
    "SLAReport",
    "Suscripcion",
    "Umbral",
    "Usuario",
]
