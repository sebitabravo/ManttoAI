"""Regresiones de la migración del proveedor JWT."""

import importlib

import pytest
from jwt import InvalidTokenError


@pytest.mark.parametrize(
    "module_name",
    (
        "app.dependencies",
        "app.routers.auth",
        "app.routers.equipos",
        "app.services.auth_service",
    ),
)
def test_jwt_consumers_use_pyjwt(module_name: str):
    """Los consumidores JWT deben usar PyJWT y su excepción común."""

    module = importlib.import_module(module_name)

    assert module.jwt.__name__ == "jwt"
    assert module.JWTError is InvalidTokenError
