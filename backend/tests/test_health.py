"""Tests del estado general del backend."""

from app import main, models, routers, schemas, services


def test_health_endpoint(client):
    """Valida el endpoint de salud del backend."""

    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_health_endpoint_reports_database_down(client, monkeypatch):
    """Valida que /health informe error cuando falla la conectividad DB."""

    monkeypatch.setattr(main, "check_database_connection", lambda: False)

    response = client.get("/ready")
    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "degraded"


def test_readiness_authenticates_redis_with_separate_password(client, monkeypatch):
    """Readiness debe usar REDIS_PASSWORD aunque REDIS_URL no tenga auth."""

    import redis

    calls = []

    class FakeRedis:
        def ping(self):
            return True

    def fake_from_url(url, **kwargs):
        calls.append({"url": url, "kwargs": kwargs})
        return FakeRedis()

    monkeypatch.setattr(main, "check_database_connection", lambda: True)
    monkeypatch.setattr(main.settings, "database_url", "sqlite:///:memory:")
    monkeypatch.setattr(main.settings, "redis_url", "redis://redis:6379")
    monkeypatch.setattr(main.settings, "redis_password", "redis-secret")
    monkeypatch.setattr(main.settings, "mqtt_enabled", False)
    monkeypatch.setattr(redis, "from_url", fake_from_url)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "components": {"db": True, "redis": True, "mqtt": True},
    }
    assert {
        "url": "redis://redis:6379",
        "kwargs": {"socket_connect_timeout": 2, "password": "redis-secret"},
    } in calls


def test_dashboard_summary(client):
    """Valida el resumen del dashboard con equipos persistidos."""

    client.post(
        "/api/v1/equipos",
        json={
            "nombre": "Compresor dashboard",
            "ubicacion": "Sala 1",
            "tipo": "Compresor",
            "estado": "operativo",
        },
    )

    response = client.get("/api/v1/dashboard/resumen")
    assert response.status_code == 200
    assert response.json()["total_equipos"] >= 1


def test_packages_are_importable():
    """Asegura que los paquetes principales carguen sin errores."""

    assert models is not None
    assert schemas is not None
    assert services is not None
    assert routers is not None
