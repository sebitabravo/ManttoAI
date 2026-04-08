"""Schemas Pydantic del proyecto."""

from app.schemas.alerta import (
    AlertaCountResponse,
    AlertaCreate,
    AlertaResponse,
    AlertaUpdate,
)
from app.schemas.dashboard import DashboardEquipoResumen, DashboardResumenResponse
from app.schemas.equipo import EquipoCreate, EquipoResponse, EquipoUpdate
from app.schemas.lectura import LecturaCreate, LecturaResponse, LecturaUpdate
from app.schemas.mantencion import (
    MantencionCreate,
    MantencionResponse,
    MantencionUpdate,
)
from app.schemas.prediccion import (
    PrediccionCreate,
    PrediccionResponse,
    PrediccionUpdate,
)
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
    "LecturaUpdate",
    "LecturaResponse",
    "AlertaCreate",
    "AlertaResponse",
    "AlertaUpdate",
    "AlertaCountResponse",
    "DashboardEquipoResumen",
    "DashboardResumenResponse",
    "PrediccionCreate",
    "PrediccionUpdate",
    "PrediccionResponse",
    "MantencionCreate",
    "MantencionUpdate",
    "MantencionResponse",
    "UmbralCreate",
    "UmbralUpdate",
    "UmbralResponse",
]
