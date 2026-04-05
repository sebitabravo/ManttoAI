"""Schemas Pydantic del proyecto."""

from app.schemas.alerta import AlertaResponse, AlertaUpdate
from app.schemas.dashboard import DashboardEquipoResumen, DashboardResumenResponse
from app.schemas.equipo import EquipoCreate, EquipoResponse, EquipoUpdate
from app.schemas.lectura import LecturaCreate, LecturaResponse
from app.schemas.mantencion import (
    MantencionCreate,
    MantencionResponse,
    MantencionUpdate,
)
from app.schemas.prediccion import PrediccionResponse
from app.schemas.umbral import UmbralCreate, UmbralResponse, UmbralUpdate
from app.schemas.usuario import LoginRequest, Token, UsuarioCreate, UsuarioResponse

__all__ = [
    "UsuarioCreate",
    "UsuarioResponse",
    "LoginRequest",
    "Token",
    "EquipoCreate",
    "EquipoUpdate",
    "EquipoResponse",
    "LecturaCreate",
    "LecturaResponse",
    "AlertaResponse",
    "AlertaUpdate",
    "DashboardEquipoResumen",
    "DashboardResumenResponse",
    "PrediccionResponse",
    "MantencionCreate",
    "MantencionUpdate",
    "MantencionResponse",
    "UmbralCreate",
    "UmbralUpdate",
    "UmbralResponse",
]
