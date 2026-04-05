"""Fixtures compartidas para pytest."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Entrega un cliente de prueba ejecutando el ciclo de vida de la API."""

    with TestClient(app) as test_client:
        yield test_client
