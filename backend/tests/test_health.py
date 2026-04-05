"""Tests del estado general del backend."""

from app import main, models, routers, schemas, services


def test_health_endpoint(client):
    """Valida el endpoint de salud del backend."""

    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"]["connected"] is True


def test_health_endpoint_reports_database_down(client, monkeypatch):
    """Valida que /health informe error cuando falla la conectividad DB."""

    monkeypatch.setattr(main, "check_database_connection", lambda: False)

    response = client.get("/health")
    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["database"]["connected"] is False


def test_dashboard_summary(client):
    """Valida el resumen demo usado por el dashboard."""

    response = client.get("/dashboard/resumen")
    assert response.status_code == 200
    assert response.json()["total_equipos"] >= 1


def test_packages_are_importable():
    """Asegura que los paquetes principales carguen sin errores."""

    assert models is not None
    assert schemas is not None
    assert services is not None
    assert routers is not None
