"""Fixtures compartidas para pytest."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Entrega un cliente de prueba para la API."""

    return TestClient(app)
