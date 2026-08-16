"""Tests unitarios para métricas con Redis + fallback en memoria."""

import asyncio
from unittest.mock import patch
from types import SimpleNamespace

import pytest
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.routers import metrics
from app.middleware.request_metrics import RequestMetricsMiddleware
from app.models.usuario import Usuario


def teardown_function() -> None:
    """Limpia estado global de métricas entre tests."""

    metrics._mem_request_count.clear()
    metrics._mem_request_duration.clear()


def test_track_request_metrics_acota_historial_de_duraciones() -> None:
    """Debe mantener buffer acotado para evitar crecimiento infinito."""

    endpoint = "unit_test_endpoint"

    @metrics.track_request_metrics(endpoint)
    async def _fake_handler() -> dict[str, str]:
        return {"status": "ok"}

    total_calls = metrics._MAX_DURATION_SAMPLES + 25
    for _ in range(total_calls):
        asyncio.run(_fake_handler())

    # Verificar usando las funciones publicas (Redis-aware)
    counts = metrics._get_all_counts()
    assert counts.get(endpoint) == total_calls

    # Verificar que el buffer en memoria esta acotado
    # (Redis puede no estar disponible en tests, asi que verificamos el fallback)
    if endpoint in metrics._mem_request_duration:
        assert (
            len(metrics._mem_request_duration[endpoint])
            == metrics._MAX_DURATION_SAMPLES
        )


def test_get_average_duration_considera_ultimos_n_registros() -> None:
    """Debe calcular promedio sobre los últimos N registros."""

    endpoint = "unit_test_average"
    metrics._mem_request_duration[endpoint] = metrics.deque(
        [0.1, 0.2, 0.3, 0.4],
        maxlen=metrics._MAX_DURATION_SAMPLES,
    )

    average = metrics._get_average_duration(endpoint, last_n=2)
    # Debe promediar los ultimos 2 valores: (0.3 + 0.4) / 2 = 0.35
    assert average == pytest.approx(0.35)


def test_request_metrics_middleware_registra_cada_request() -> None:
    """El middleware debe alimentar el resumen, no solo escribir logs."""

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/v1/dashboard/resumen",
        "raw_path": b"/api/v1/dashboard/resumen",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 1234),
        "server": ("localhost", 8000),
        "scheme": "http",
    }
    request = Request(scope)
    middleware = RequestMetricsMiddleware(app=None)

    async def call_next(_request: Request) -> Response:
        return Response(status_code=200)

    async def exercise() -> None:
        with patch("app.routers.metrics._record_metrics") as record_metrics:
            await middleware.dispatch(request, call_next)
            record_metrics.assert_called_once()
            endpoint, duration = record_metrics.call_args.args
            assert endpoint == "/api/v1/dashboard/resumen"
            assert duration >= 0

    asyncio.run(exercise())


def test_detailed_health_does_not_expose_database_exception(
    monkeypatch,
) -> None:
    """El health check debe ocultar hosts/credenciales de errores SQLAlchemy."""

    class FailingDB:
        def execute(self, _query):
            raise SQLAlchemyError("mysql://user:secret@example.internal:3306/db")

    monkeypatch.setattr(metrics, "_get_redis", lambda: None)

    result = asyncio.run(
        metrics.get_detailed_health(
            request=SimpleNamespace(),
            db=FailingDB(),
        )
    )

    assert result["components"]["database"] == {
        "status": "unhealthy",
        "message": "Database unavailable",
    }


def test_metrics_operational_endpoints_are_admin_only(client) -> None:
    """La observabilidad de infraestructura no debe quedar expuesta a técnicos."""

    session_local = client.app.state.testing_session_local
    with session_local() as db:
        user = db.scalars(
            select(Usuario).where(Usuario.email == "admin@manttoai.local")
        ).first()
        assert user is not None
        user.rol = "visualizador"
        db.commit()

    for path in ("/api/v1/metrics/summary", "/api/v1/metrics/health-detailed"):
        response = client.get(path)
        assert response.status_code == 403
