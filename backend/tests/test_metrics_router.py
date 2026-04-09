"""Tests unitarios para métricas en memoria del router."""

import asyncio

import pytest

from app.routers import metrics


def teardown_function() -> None:
    """Limpia estado global de métricas entre tests."""

    metrics._request_count.clear()
    metrics._request_duration.clear()
    metrics._active_users.clear()


def test_track_request_metrics_acota_historial_de_duraciones() -> None:
    """Debe mantener buffer acotado para evitar crecimiento infinito."""

    endpoint = "unit_test_endpoint"

    @metrics.track_request_metrics(endpoint)
    async def _fake_handler() -> dict[str, str]:
        return {"status": "ok"}

    total_calls = metrics._MAX_DURATION_SAMPLES_PER_ENDPOINT + 25
    for _ in range(total_calls):
        asyncio.run(_fake_handler())

    assert metrics._request_count[endpoint] == total_calls
    assert (
        len(metrics._request_duration[endpoint])
        == metrics._MAX_DURATION_SAMPLES_PER_ENDPOINT
    )


def test_get_average_duration_considera_ultimos_n_registros() -> None:
    """Debe calcular promedio sobre los últimos N registros del deque."""

    endpoint = "unit_test_average"
    metrics._request_duration[endpoint] = metrics.deque(
        [0.1, 0.2, 0.3, 0.4],
        maxlen=metrics._MAX_DURATION_SAMPLES_PER_ENDPOINT,
    )

    average = metrics.get_average_duration(endpoint, last_n=2)
    assert average == pytest.approx(0.35)
